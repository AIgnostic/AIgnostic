import React, {
  createContext,
  useState,
  useCallback,
  useEffect,
  useRef,
  MutableRefObject,
} from 'react';
import { v4 as uuidv4 } from 'uuid';
import { WEBSOCKET_URL } from '../constants';

interface UserIdSocketContextProps {
  userId: string;
  socket: WebSocket | null;
  refreshUserId: () => void;
  disconnectRef: MutableRefObject<boolean>;
  closeSocket: () => void;
}

const UserIdSocketContext = createContext<UserIdSocketContextProps>({
  userId: '',
  socket: null,
  refreshUserId: () => {}, // eslint-disable-line @typescript-eslint/no-empty-function
  disconnectRef: undefined as unknown as MutableRefObject<boolean>,
  closeSocket: () => {}, // eslint-disable-line @typescript-eslint/no-empty-function
});

export function UserIdSocketProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [userID, setUserID] = useState(uuidv4());
  const [socket, setSocket] = useState(() => new WebSocket(WEBSOCKET_URL));
  const disconnectRef = useRef(false);

  const refreshUserId = useCallback(() => {
    const id = uuidv4();
    setUserID(id);
  }, []);

  const createSetSocket = useCallback(() => {
    const sock = new WebSocket(WEBSOCKET_URL);
    // Need to pass function to setSocket to avoid stale closure
    setSocket((oldSock) => {
      if (oldSock) {
        oldSock.close();
      }
      return sock;
    });
    return sock;
  }, []);

  const initSocket = useCallback(
    (userID: string) => {
      const sock = createSetSocket();

      // Connection logic
      sock.onopen = function () {
        console.log('WebSocket connection established');
        this.send(userID.toString());
      };
      sock.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received message:', data);
      };

      sock.onclose = () => {
        if (!disconnectRef.current) {
          // only attempt to reconnect if disconnect was not intentional
          console.log(
            'WebSocket connection closed, attempting to reconnect...'
          );
          setTimeout(() => initSocket(userID), 1000);
        }
      };
    },
    [createSetSocket]
  );

  // On boot create socket
  useEffect(() => {
    initSocket(userID);
  }, [initSocket, userID]);

  const closeSocket = useCallback(() => {
    if (socket) {
      disconnectRef.current = true;
      socket.close();
    }
  }, [socket]);

  return (
    <UserIdSocketContext.Provider
      value={{
        userId: userID,
        socket,
        refreshUserId,
        disconnectRef,
        closeSocket,
      }}
    >
      {children}
    </UserIdSocketContext.Provider>
  );
}

export const useUser = () => React.useContext(UserIdSocketContext);

export default UserIdSocketProvider;
