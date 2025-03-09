import { MutableRefObject, useEffect, useRef, useState } from "react";

const connectWebSocket = (
    webSocketUrl: string,
    userId: string,
    disconnectRef: MutableRefObject<boolean>
) => {
    const newSocket = new WebSocket(webSocketUrl);
    newSocket.onopen = () => {
        console.log('WebSocket connection established');
        newSocket.send(userId.toString());
    };
    newSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
    };

    newSocket.onclose = () => {
        if (!disconnectRef.current) {
            // only attempt to reconnect if disconnect was not intentional
            console.log(
                'WebSocket connection closed, attempting to reconnect...'
            );
            setTimeout(() => connectWebSocket(webSocketUrl, userId, disconnectRef), 1000);
        }
    };

    return newSocket;
};

export default connectWebSocket;
