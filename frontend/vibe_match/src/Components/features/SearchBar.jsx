import { Search  } from "lucide-react";


export default function SearchBar({
    query,
    setQuery,
    hasSearched,
    searchEvents,
    resetSearch
}){

    return (

        <div className={`flex justify-center w-full transition-all duration-500 ${
        hasSearched ? "mt-5" : "mt-[35vh]"
        }`}>
            <div className="relative w-[550px] max-w-[90%]">

                <input className="w-full py-[14px] pr-[110px] pl-[40px] text-[16px] rounded-full border border-white bg-white text-black outline-none"
                    type="text"
                    placeholder="Describe tu plan ideal aquí..."
                    value = {query}
                    onChange={(e)=>{setQuery(e.target.value)}}
                    onKeyDown={(e)=> e.key ==="Enter" && searchEvents()
                    }
                
                
                
                />

                <button>

                </button>

                <button>


                </button>

            </div>


        </div>

    );


};