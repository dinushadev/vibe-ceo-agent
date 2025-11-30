import { useState, useEffect, useRef, useCallback } from 'react';

interface UseVoiceReturn {
    isListening: boolean;
    isProcessing: boolean;
    transcript: string;
    volume: number;
    startRecording: () => Promise<void>;
    stopRecording: () => void;
    error: string | null;
}

export function useVoice(): UseVoiceReturn {
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [volume, setVolume] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const websocketRef = useRef<WebSocket | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const isListeningRef = useRef(false);

    // Audio Queue Management
    const audioQueueRef = useRef<string[]>([]);
    const isPlayingRef = useRef(false);

    const connectWebSocket = useCallback(() => {
        if (websocketRef.current?.readyState === WebSocket.OPEN) return;

        const wsUrl = 'ws://localhost:8000/api/live-stream';
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Voice WebSocket connected');
            setError(null);

            // Send initial configuration with timezone
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            ws.send(JSON.stringify({
                type: 'config',
                payload: { timezone }
            }));
        };

        ws.onmessage = async (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'transcript') {
                    setTranscript(data.payload.text);
                    if (data.payload.is_final) {
                        setIsProcessing(true);
                    }
                } else if (data.type === 'agent_response') {
                    setIsProcessing(false);
                    // Optional: Display agent text response
                } else if (data.type === 'audio_response') {
                    console.log('Received audio response, adding to queue');
                    // Add to queue instead of playing immediately
                    audioQueueRef.current.push(data.payload);
                    processAudioQueue();
                }
            } catch (err) {
                console.error('Error parsing WS message:', err);
            }
        };

        ws.onerror = (event) => {
            console.error('WebSocket error:', event);
            setError('Connection error');
            setIsListening(false);
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
        };

        websocketRef.current = ws;
    }, []);

    const processAudioQueue = async () => {
        if (isPlayingRef.current || audioQueueRef.current.length === 0) return;

        isPlayingRef.current = true;
        const nextAudio = audioQueueRef.current.shift();

        if (nextAudio) {
            await playAudio(nextAudio);
            // Continue processing queue
            processAudioQueue();
        } else {
            isPlayingRef.current = false;
        }
    };

    const playAudio = async (base64Audio: string): Promise<void> => {
        return new Promise(async (resolve) => {
            try {
                // Decode base64 to raw binary
                const audioData = atob(base64Audio);
                const arrayBuffer = new ArrayBuffer(audioData.length);
                const view = new Uint8Array(arrayBuffer);
                for (let i = 0; i < audioData.length; i++) {
                    view[i] = audioData.charCodeAt(i);
                }

                if (!audioContextRef.current) {
                    audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
                        sampleRate: 24000, // Gemini Native Audio standard
                    });
                }

                // Ensure context is running
                if (audioContextRef.current.state === 'suspended') {
                    await audioContextRef.current.resume();
                }

                // Convert raw PCM (Int16) to AudioBuffer (Float32)
                // Gemini sends 16-bit PCM, Little Endian
                const int16Data = new Int16Array(arrayBuffer);
                const float32Data = new Float32Array(int16Data.length);

                for (let i = 0; i < int16Data.length; i++) {
                    // Normalize Int16 (-32768 to 32767) to Float32 (-1.0 to 1.0)
                    float32Data[i] = int16Data[i] / 32768.0;
                }

                // Create AudioBuffer
                const audioBuffer = audioContextRef.current.createBuffer(
                    1, // Mono
                    float32Data.length,
                    24000 // Sample Rate (Must match Gemini output)
                );

                // Copy data to channel
                audioBuffer.getChannelData(0).set(float32Data);

                // Play buffer
                const source = audioContextRef.current.createBufferSource();
                source.buffer = audioBuffer;
                source.connect(audioContextRef.current.destination);

                source.onended = () => {
                    isPlayingRef.current = false;
                    resolve();
                };

                source.start(0);
            } catch (err) {
                console.error('Error playing audio:', err);
                isPlayingRef.current = false;
                resolve();
            }
        });
    };

    const startRecording = async () => {
        try {
            setError(null);

            // Ensure WebSocket is connected
            if (!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) {
                connectWebSocket();
            }

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
                sampleRate: 16000, // Request 16kHz
            });
            audioContextRef.current = audioContext;

            const source = audioContext.createMediaStreamSource(stream);
            const processor = audioContext.createScriptProcessor(4096, 1, 1);

            processor.onaudioprocess = (e) => {
                if (!isListeningRef.current) return;

                const inputData = e.inputBuffer.getChannelData(0);

                // Calculate RMS volume
                let sum = 0;
                for (let i = 0; i < inputData.length; i++) {
                    sum += inputData[i] * inputData[i];
                }
                const rms = Math.sqrt(sum / inputData.length);
                setVolume(Math.min(1, rms * 5));

                // Convert float32 to int16
                const pcmData = new Int16Array(inputData.length);
                for (let i = 0; i < inputData.length; i++) {
                    pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
                }

                // Send to WebSocket
                if (websocketRef.current?.readyState === WebSocket.OPEN) {
                    const buffer = pcmData.buffer;
                    const bytes = new Uint8Array(buffer);
                    const len = bytes.byteLength;
                    let binaryStr = '';
                    for (let i = 0; i < len; i++) {
                        binaryStr += String.fromCharCode(bytes[i]);
                    }
                    const base64 = btoa(binaryStr);

                    websocketRef.current.send(JSON.stringify({
                        type: 'audio_chunk',
                        payload: base64
                    }));
                }
            };

            source.connect(processor);

            // CRITICAL FIX: Connect to a GainNode with 0 gain before destination
            // This allows the ScriptProcessor to run (needed for Chrome) but prevents
            // the user from hearing their own voice (input monitoring).
            const gainNode = audioContext.createGain();
            gainNode.gain.value = 0;
            processor.connect(gainNode);
            gainNode.connect(audioContext.destination);

            // Store references to cleanup
            (mediaRecorderRef as any).current = {
                stop: () => {
                    processor.disconnect();
                    gainNode.disconnect();
                    source.disconnect();
                    stream.getTracks().forEach(track => track.stop());
                }
            };

            setIsListening(true);
            isListeningRef.current = true;

        } catch (err) {
            console.error('Error starting recording:', err);
            setError('Could not access microphone');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            (mediaRecorderRef.current as any).stop();
        }
        setIsListening(false);
        isListeningRef.current = false;
        setVolume(0); // Reset volume when stopped
    };

    useEffect(() => {
        connectWebSocket();
        return () => {
            if (websocketRef.current) {
                websocketRef.current.close();
            }
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
        };
    }, [connectWebSocket]);

    return {
        isListening,
        isProcessing,
        transcript,
        volume,
        startRecording,
        stopRecording,
        error
    };
}
