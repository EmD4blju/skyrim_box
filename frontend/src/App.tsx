import { useItems } from './hooks/useItems';
import heroBanner from './assets/hero_banner.jpg';

function App() {
  const { data: items, isLoading, isError } = useItems();

  return (
    <div className="min-h-screen bg-stone-900 text-gray-200 font-serif">
      {/* Hero Banner */}
      <div 
        className="relative w-full h-125 bg-cover bg-center flex items-center justify-center border-b-4 border-yellow-700"
        style={{ backgroundImage: `url(${heroBanner})` }} 
      >
        <div className="absolute inset-0 bg-black/60"></div>
        <div className="relative z-10 text-center px-4">
          <h1 className="text-5xl md:text-7xl font-bold tracking-widest text-gray-100 uppercase drop-shadow-lg mb-4">
            Skyrim Box
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 italic max-w-2xl mx-auto drop-shadow-md">
            "I used to be an engineer like you, then I took a bug in the knee." 
            <br /> Explore artifacts and leave your mark on Tamriel.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto py-12 px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold uppercase tracking-wider text-yellow-600 mb-2">Relics of Tamriel</h2>
          <div className="w-24 h-1 bg-yellow-700 mx-auto rounded"></div>
        </div>

        {isLoading && (
          <div className="text-center text-xl text-gray-400 py-12 animate-pulse">
            Summoning items from the void...
          </div>
        )}

        {isError && (
          <div className="text-center text-xl text-red-500 py-12">
            By the Nine Divines! Something went wrong fetching the items. Check if your API is running.
          </div>
        )}

        {items && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {items.map((item) => (
              <div 
                key={item.id} 
                className="bg-stone-800 border border-stone-700 rounded-lg overflow-hidden shadow-2xl hover:border-yellow-600 transition-all duration-300 group cursor-pointer"
              >
                <div className="h-48 bg-stone-700 flex items-center justify-center relative overflow-hidden">
                   {/* Optional graphic placeholder depending on name */}
                   <div className="absolute inset-0 bg-stone-900/40 group-hover:bg-stone-900/10 transition-colors z-10"></div>
                   <span className="text-7xl group-hover:scale-125 transition-transform duration-500 z-0">
                    {item.name.toLowerCase().includes('sword') ? '🗡️' : 
                     item.name.toLowerCase().includes('sweetroll') ? '🧁' : '✨'}
                  </span>
                </div>
                <div className="p-6">
                  <h3 className="text-2xl font-bold text-yellow-500 mb-2">{item.name}</h3>
                  <p className="text-gray-400 italic">"{item.description}"</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
