"use client";

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

import { useState, useRef, useEffect } from "react";

export default function AudioRecorder() {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [audioUrl, setAudioUrl] = useState<string | null>(null); // 🔹 Stores recorded audio URL
  const [amplitude, setAmplitude] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  const startRecording = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      alert("Your browser does not support tab audio recording.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ audio: true });

      const audioTracks = stream.getAudioTracks();
      if (audioTracks.length === 0) {
        console.error("No audio track found in the stream.");
        alert("No audio track detected. Make sure tab audio is playing.");
        return;
      }

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // 🎵 Audio Processing
      audioContextRef.current = new AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(new MediaStream([audioTracks[0]]));
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);

      visualizeAudio();

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url); // 🔹 Save audio URL for playback & download
        transcribeAudio(audioBlob);
        stopVisualizer();
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (error) {
      console.error("Error accessing tab audio:", error);
      alert("Failed to access tab audio. Make sure to allow permissions and play some audio in the tab.");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append("file", audioBlob, "audio.wav");
    formData.append("model", "whisper-1");

    try {
      const response = await fetch("https://api.openai.com/v1/audio/transcriptions", {
        method: "POST",
        headers: {
          Authorization: `Bearer YOUR_OPENAI_API_KEY`, // Replace with your API key
        },
        body: formData,
      });

      const data = await response.json();
      setTranscript(data.text || "Transcription failed.");
    } catch (error) {
      console.error("Whisper API Error:", error);
      setTranscript("Error transcribing audio.");
    }
  };

  // 🎵 Audio Visualization
  const visualizeAudio = () => {
    if (!analyserRef.current) return;
    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const updateAmplitude = () => {
      analyserRef.current?.getByteFrequencyData(dataArray);
      const avgAmplitude = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
      setAmplitude(avgAmplitude);
      animationFrameRef.current = requestAnimationFrame(updateAmplitude);
    };

    updateAmplitude();
  };

  const stopVisualizer = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    setAmplitude(0);
  };

  return (
    <div className="p-6 flex flex-col items-center">
      <h1 className="text-xl font-bold mb-4">Tab Audio Recorder</h1>

      {/* 🎵 Music Line Visualizer */}
      <div className="relative w-40 h-20 flex items-center">
        {[...Array(10)].map((_, i) => (
          <div
            key={i}
            className="w-2 bg-blue-500 mx-1 transition-all duration-75"
            style={{
              height: `${Math.random() * amplitude}px`,
            }}
          ></div>
        ))}
      </div>

      {/* 🎙️ Start / Stop Recording */}
      <button
        onClick={recording ? stopRecording : startRecording}
        className="px-4 py-2 mt-4 rounded bg-blue-500 text-white"
      >
        {recording ? "Stop Recording" : "Start Recording"}
      </button>

      {/* 🔊 Show Audio Player if Recorded */}
      {audioUrl && (
        <div className="mt-4">
          <h2 className="text-lg font-semibold">Recorded Audio:</h2>
          <audio controls className="mt-2">
            <source src={audioUrl} type="audio/wav" />
            Your browser does not support the audio element.
          </audio>
          <a
            href={audioUrl}
            download="recording.wav"
            className="mt-2 block text-blue-600 underline"
          >
            ⬇️ Download Recording
          </a>
        </div>
      )}

      {/* 📝 Transcription Output */}
      {transcript && (
        <p className="mt-4 p-2 bg-gray-200 rounded">{transcript}</p>
      )}
    </div>
  );
}
