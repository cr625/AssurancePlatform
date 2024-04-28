'use client'

import { ChevronDown, Database } from 'lucide-react';
import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';

function EvidenceNode({ data }: any) {
  return (
    <div className={`px-4 py-2 shadow-md rounded-md bg-emerald-600 text-white`}>
      <div className="flex">
        <div className="rounded-full w-12 h-12 flex justify-center items-center bg-emerald-800/30">
          <Database />
        </div>
        <div className="ml-2 w-[200px]">
          <div className="text-lg font-bold">{data.name}<span className='text-xs ml-2'>({data.identifier})</span></div>
          <div className="text-xs truncate">{data.description}</div>
        </div>
      </div>

      <Handle type="target" position={Position.Top} />
      {/* <Handle type="source" position={Position.Bottom} /> */}
    </div>
  );
}

export default memo(EvidenceNode);
