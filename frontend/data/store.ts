'use client'

import { create } from 'zustand';
import {
  Connection,
  Edge,
  EdgeChange,
  Node,
  NodeChange,
  addEdge,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
  applyNodeChanges,
  applyEdgeChanges,
  NodeTypes,
} from 'reactflow';
import { initNodes } from './nodes';
import { initEdges } from './edges';
import { nodeTypes } from './nodeTypes';
import Dagre from '@dagrejs/dagre';

type Store = {
  assuranceCase: any;
  nodes: Node[];
  edges: Edge[];
  nodeTypes: NodeTypes;
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  setAssuranceCase: (assuranceCase: any) => void;
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  layoutNodes: (nodes: Node[], edges: Edge[]) => void;
};

export type NodeData = {
  color: string;
};

// Define a function to layout nodes vertically using Dagre
const layoutNodesVertically = (nodes: Node[], edges: Edge[]) => {
  const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

  g.setGraph({ rankdir: 'TB' });

  edges.forEach((edge: Edge) => g.setEdge(edge.source, edge.target));
  nodes.forEach((node: Node | any) => g.setNode(node.id, node));

  Dagre.layout(g);

  return {
    nodes: nodes.map((node: any, index: any) => {
      const { x, y } = g.node(node.id);
      return { ...node, position: { x, y } };
    }),
    edges,
  };
};

// this is our useStore hook that we can use in our components to get parts of the store and call actions
const useStore = create<Store>((set, get) => ({
  assuranceCase: null,
  nodes: initNodes,
  edges: initEdges,
  nodeTypes: nodeTypes,
  onNodesChange: (changes: NodeChange[]) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },
  onEdgesChange: (changes: EdgeChange[]) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },
  onConnect: (connection: Connection) => {
    set({
      edges: addEdge(connection, get().edges),
    });
  },
  setAssuranceCase: (assuranceCase: any) => {
    set({ assuranceCase })
  },
  setNodes: (nodes: Node[]) => {
    // const { nodes: layoutedNodes } = layoutNodesVertically(nodes, []);
    set({ nodes });
  },
  setEdges: (edges: Edge[]) => {
    set({ edges });
  },
  fitView: () => {}, // Define fitView function
  layoutNodes: (nodes: Node[], edges: Edge[]) => {
    // Layout nodes vertically
    const { nodes: layoutedNodes, edges: layoutedEdges } = layoutNodesVertically(nodes, edges);

    // Set the layouted nodes and edges
    set({ nodes: layoutedNodes, edges: layoutedEdges });
  },
}));

export default useStore;
