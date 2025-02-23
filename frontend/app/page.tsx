"use client"

import { useState, useEffect } from 'react';
import UploadGif from '@/app/components/UploadGif';

export default function Home() {

  const [currentGif, setCurrentGif] = useState(null);
  const [gifs, setGifs] = useState([]);

  useEffect(() => {
    const fetchCurrentGif = async () => {
      try {
        const response = await fetch('http://blinken.local:5050/current');
        const { current_gif } = await response.json();
        setCurrentGif(current_gif);
      } catch (error) {
        console.error('Error fetching current GIF:', error);
      }
    };

    const fetchGifList = async () => {
      try {
        const response = await fetch('http://blinken.local:5050/list');
        const { gifs } = await response.json();
        setGifs(gifs);
      } catch (error) {
        console.error('Error fetching current GIF list:', error);
      }
    };

    // Fetch current GIF immediately and then every 2 seconds
    fetchCurrentGif();
    const currentGifIntervalId = setInterval(fetchCurrentGif, 2000);

    // Fetch current GIF List immediately and then every 5 seconds
    fetchGifList();
    const gifListIntervalId = setInterval(fetchGifList, 5000);

    // Cleanup on component unmount
    return () => {
      clearInterval(currentGifIntervalId);
      clearInterval(gifListIntervalId);
    }
  }, []);

  const handleDelete = async (gif: string) => {
    // Ask for confirmation
    const isConfirmed = window.confirm(`Are you sure you want to delete "${gif}"?`);

    if (isConfirmed) {
      try {
        // Call the DELETE endpoint in your API to delete the GIF
        const response = await fetch(`http://blinken.local:5050/delete/${gif}`, {
          method: 'DELETE',
        });

        if (response.ok) {
          setGifs(gifs.filter(gifName => gifName !== gif));
        } else {
          alert(`Failed to delete "${gif}".`);
        }
      } catch (error) {
        console.error("Error deleting the GIF:", error);
        alert("There was an error deleting the GIF.");
      }
    }
  };

  const gifList = gifs.map(gif => 
    <div key={gif} className="flex flex-col justify-between items-center">
        <img
            src={`http://blinken.local:5050/gif/${gif}`}
            alt={gif}
            className="w-auto h-48 object-contain rounded-lg shadow-lg"
            onClick={() => handleDelete(gif)}
        />
      <p className="mt-2 text-center text-white font-semibold">{gif}</p>
    </div>
  )

  return (
    <div className="">
      <main className="">
        <div className="current-gif bg-gray-800 text-white py-2 text-center text-lg font-medium">
          {currentGif ? `Currently displaying: ${currentGif}` : "No GIF currently displaying"}

          <div className="flex flex-col justify-between items-center">
            <img
              src={`http://blinken.local:5050/gif/${currentGif}`}
              alt={currentGif}
              className="w-auto h-32 object-contain rounded-lg shadow-lg"
            />
            <p className="mt-2 text-center text-white font-semibold">{currentGif}</p>
          </div>
        </div>

        <div className="top-uploader flex flex-col items-center gap-4">
            <UploadGif />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {gifList}
        </div>
      </main>
      <footer className="">
        <UploadGif />
      </footer>
    </div>
  );
}
