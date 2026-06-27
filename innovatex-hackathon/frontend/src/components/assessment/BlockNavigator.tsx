import type { Block, BlockId } from '@/types'

interface BlockNavigatorProps {
  blocks: Block[]
  activeBlock: BlockId
  onSelect: (id: BlockId) => void
  blockCompletion: Record<BlockId, boolean>
}

export default function BlockNavigator({
  blocks,
  activeBlock,
  onSelect,
  blockCompletion,
}: BlockNavigatorProps) {
  return (
    <div className="flex border-b border-slate-200 bg-white">
      {blocks.map((block) => {
        const isActive = block.id === activeBlock
        const isCompleted = blockCompletion[block.id]
        const classes = [
          'block-tab',
          isActive ? 'active' : '',
          isCompleted && !isActive ? 'completed' : '',
        ]
          .filter(Boolean)
          .join(' ')
        return (
          <button
            key={block.id}
            type="button"
            className={classes}
            onClick={() => onSelect(block.id)}
          >
            {isCompleted && (
              <span className="mr-1" aria-hidden>
                ✓
              </span>
            )}
            <span>{block.title}</span>
            <span className="block text-xs font-normal text-slate-400 mt-0.5">
              {block.weight}%
            </span>
          </button>
        )
      })}
    </div>
  )
}