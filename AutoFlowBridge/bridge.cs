using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace WebSocketClient
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // Create a client websocket
            ClientWebSocket ws = new ClientWebSocket();

            // Connect to the websocket server at port 8001
            Uri uri = new Uri("ws://localhost:8001/");
            await ws.ConnectAsync(uri, CancellationToken.None);

            // Start a task to receive messages from the server
            Task receiveTask = ReceiveMessages(ws);

            // Wait for the user to press any key to exit
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();

            // Close the websocket connection gracefully
            await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Bye", CancellationToken.None);
        }

        // A method that receives messages from the server and prints them to the console
        static async Task ReceiveMessages(ClientWebSocket ws)
        {
            // Create a buffer to store the received data
            byte[] buffer = new byte[1024];

            // Loop until the websocket is closed
            while (ws.State == WebSocketState.Open)
            {
                // Receive a message from the server
                WebSocketReceiveResult result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);

                // If the message is text, decode it and print it
                if (result.MessageType == WebSocketMessageType.Text)
                {
                    string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    Console.WriteLine($"Received: {message}");
                }
                // If the message is close, break the loop
                else if (result.MessageType == WebSocketMessageType.Close)
                {
                    break;
                }
            }
        }
    }
}
