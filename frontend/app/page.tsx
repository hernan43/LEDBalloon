"use client"

import { useState, useEffect } from 'react';

export default function Home() {

  const [currentGif, setCurrentGif] = useState(null);

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

    // Fetch current GIF immediately and then every 2 seconds
    fetchCurrentGif();
    const intervalId = setInterval(fetchCurrentGif, 2000);

    // Cleanup on component unmount
    return () => clearInterval(intervalId);
  }, []);


  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-8 items-center sm:items-start">
      Screen is currently displaying: {currentGif || "Loading..."}
      </main>
      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
      	Foot
      </footer>
    </div>
  );
}
