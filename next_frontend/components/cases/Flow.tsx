'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useReactFlow,
} from 'reactflow';

import 'reactflow/dist/style.css';
import NodeEdit from '@/components/common/NodeEdit';
import ActionButtons from './ActionButtons';

import useStore from '@/data/store';
import { Loader2, Unplug, X } from 'lucide-react';
import { convertAssuranceCase } from '@/lib/convert-case';
import { getLayoutedElements } from '@/lib/layout-helper';

import 'react-toastify/dist/ReactToastify.css';
import { useTheme } from 'next-themes';
import { useToast } from '../ui/use-toast';
import { Button } from '../ui/button';

interface FlowProps {}

function Flow({}: FlowProps) {
  const { fitView } = useReactFlow();
  const {
    nodes,
    edges,
    nodeTypes,
    onNodesChange,
    setNodes,
    setEdges,
    layoutNodes,
    assuranceCase,
    orphanedElements
  } = useStore();
  const [editOpen, setEditOpen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<Node | any>(null);
  const [loading, setLoading] = useState(true);
  const [showOrphanMessage, setShowOrphanMessage] = useState<boolean>(true)

  const { toast } = useToast();

  const onLayout = (direction: any) => {
    const layouted = getLayoutedElements(nodes, edges, { direction });

    setNodes(layouted.nodes);
    setEdges(layouted.edges);

    window.requestAnimationFrame(() => {
      fitView();
    });
  };

  const convert = async () => {
    if (assuranceCase && assuranceCase.goals) {
      const result = await convertAssuranceCase(assuranceCase);
      const { caseNodes, caseEdges } = result;

      // Send new nodes & edges to layout function
      layoutNodes(caseNodes, caseEdges);
      setLoading(false);
    }
  };

  // intial conversion of the assurance case on component render
  useEffect(() => {
    convert();
  }, [assuranceCase]);

  const handleNodeClick = (event: React.MouseEvent, node: Node | any) => {
    setSelectedNode(node);
    setEditOpen(true);
  };

  const showCreateGoal = nodes.length > 0 && nodes[0].type === 'goal' ? false : true;

  const notify = (message: string) => {
    toast({
      description: message,
    });
  };

  const notifyError = (message: string) => {
    toast({
      variant: 'destructive',
      title: 'Uh oh! Something went wrong.',
      description: message,
    });
  };

  const reactFlowWrapper = useRef(null);

  return (
    <div className="min-h-screen">
      {loading ? (
        <div className="flex justify-center items-center min-h-screen">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      ) : (
        <div id="ChartFlow" ref={reactFlowWrapper}>
          <ReactFlow
            id="ReactFlow"
            nodes={nodes}
            edges={edges}
            onNodeClick={handleNodeClick}
            onNodesChange={onNodesChange}
            className="min-h-screen"
            fitView
            nodeTypes={nodeTypes}
            nodesDraggable={false}
          >
            <Controls className="z-50" />
            <Background />
          </ReactFlow>
          <ActionButtons
            showCreateGoal={showCreateGoal}
            actions={{ onLayout }}
            notify={notify}
            notifyError={notifyError}
          />
          <NodeEdit node={selectedNode} isOpen={editOpen} setEditOpen={setEditOpen} />
          {orphanedElements && orphanedElements.length > 0 && showOrphanMessage && (
            <div className='absolute top-16 px-8 py-2 left-0 w-full bg-slate-200/30 dark:bg-violet-500/30 text-foreground backdrop-blur-sm'>
              <div className='flex justify-center items-center'>
                <div className='container mx-auto flex justify-center items-center gap-2'>
                  <Unplug className='w-4 h-4'/>
                  <p>You have orphaned elements for this assurance case.</p>
                </div>
                <Button
                  variant={'ghost'}
                  size={'icon'}
                  className='hover:bg-gray-400/10 dark:hover:bg-slate-900/10'
                  onClick={() => setShowOrphanMessage(false)}
                >
                  <X className='w-4 h-4'/>
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Flow;
