import { useState } from 'react';
import { useComments, useAddComment } from '../hooks/useComments';
import type { Item } from '../types';

interface ItemModalProps {
  item: Item;
  onClose: () => void;
}

export const ItemModal = ({ item, onClose }: ItemModalProps) => {
  const { data: comments, isLoading, isError } = useComments(item.id);
  const [showInput, setShowInput] = useState(false);
  const [showAllComments, setShowAllComments] = useState(false);
  const [commentText, setCommentText] = useState('');
  const addCommentMutation = useAddComment();

  const handleSubmit = () => {
    if (!commentText.trim()) return;
    addCommentMutation.mutate(
      { itemId: item.id, content: commentText },
      {
        onSuccess: () => {
          setCommentText('');
          setShowInput(false);
        },
      }
    );
  };

  // Close modal when clicking on the background overlay
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 px-4 backdrop-blur-sm"
      onClick={handleOverlayClick}
    >
      <div className="bg-stone-900 border-2 border-yellow-700 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative font-serif">
        <button 
          onClick={onClose}
          className="absolute top-4 right-5 text-gray-400 hover:text-yellow-500 text-4xl leading-none transition-colors"
        >
          &times;
        </button>
        
        <div className="p-8">
          <div className="flex items-center gap-6 mb-6">
            <div className="shrink-0 w-24 h-24 bg-stone-800 rounded-full border border-stone-700 flex items-center justify-center text-5xl">
              {item.name.toLowerCase().includes('sword') ? '🗡️' : 
               item.name.toLowerCase().includes('sweetroll') ? '🧁' : '✨'}
            </div>
            <div>
              <h2 className="text-4xl font-bold text-yellow-500 mb-2">{item.name}</h2>
              <p className="text-lg text-gray-300 italic">"{item.description}"</p>
            </div>
          </div>
          
          <hr className="border-stone-700 my-8" />
          
          <h3 className="text-2xl font-bold text-gray-200 mb-6 uppercase tracking-widest text-center">Tales & Whispers</h3>
          
          <div className="mb-6">
            {!showInput ? (
              <button 
                onClick={() => setShowInput(true)}
                className="w-full py-3 border-2 border-dashed border-stone-600 text-stone-400 rounded-lg hover:border-yellow-600 hover:text-yellow-500 transition-colors text-lg font-bold"
              >
                + Scribe a new tale
              </button>
            ) : (
              <div className="bg-stone-800 p-4 rounded-lg border border-yellow-700/50">
                <textarea
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  placeholder="Share your experience with this artifact..."
                  className="w-full bg-stone-900 border border-stone-700 rounded-md p-3 text-gray-200 focus:outline-none focus:border-yellow-600 min-h-25 mb-3 resize-y"
                  autoFocus
                />
                <div className="flex justify-end gap-3">
                  <button 
                    onClick={() => {
                      setShowInput(false);
                      setCommentText('');
                    }}
                    className="px-4 py-2 text-stone-400 hover:text-gray-200 transition-colors"
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleSubmit}
                    disabled={addCommentMutation.isPending || !commentText.trim()}
                    className="px-6 py-2 bg-yellow-700 hover:bg-yellow-600 text-white rounded-md font-bold transition-colors disabled:opacity-50"
                  >
                    {addCommentMutation.isPending ? 'Scribing...' : 'Publish Tale'}
                  </button>
                </div>
              </div>
            )}
          </div>

          {isLoading && (
            <div className="text-center py-8 text-gray-400 animate-pulse">
              Reading the Elder Scrolls...
            </div>
          )}
          
          {isError && (
            <div className="text-center py-8 text-red-500">
              By the Nine Divines! Failed to decipher the scrolls.
            </div>
          )}
          
          {comments && comments.length === 0 && (
            <div className="text-center py-8 text-stone-500 italic">
              No one has spoken of this yet. Be the first to leave a mark.
            </div>
          )}
          
          {comments && comments.length > 0 && (
            <div className="space-y-4">
              {(showAllComments ? comments : comments.slice(0, 4)).map((comment) => (
                <div key={comment.id} className="bg-stone-800 p-5 rounded border border-stone-700 shadow-inner">
                  <p className="text-gray-300 text-lg">"{comment.content}"</p>
                  <p className="text-sm text-yellow-600 mt-3 text-right font-bold flex justify-end items-center gap-2">
                    <span>- Adventurer #{comment.user_id}</span>
                    <span className="text-stone-500 font-normal text-xs">
                      {comment.created_at ? new Date(comment.created_at).toLocaleString() : 'Unknown era'}
                    </span>
                  </p>
                </div>
              ))}
              
              {comments.length > 4 && !showAllComments && (
                <button 
                  onClick={() => setShowAllComments(true)}
                  className="w-full mt-4 py-2 border-t border-stone-700 text-yellow-600 hover:text-yellow-500 hover:underline text-sm font-bold tracking-wider uppercase transition-colors"
                >
                  Unveil older scrolls ({comments.length - 4} more)...
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
