using Websocket.Client;

namespace AutoFlowBridge;

class Program
{
    static async Task Main(string[] args)
    {
        var url = new Uri("ws://localhost:8001/");
        var exitEvent = new ManualResetEvent(false);

        try
        {
            using var client = new WebsocketClient(url);
            client.MessageReceived.Subscribe(msg => { Console.WriteLine("Message received: " + msg); });
            await client.Start();
            exitEvent.WaitOne();
        }
        catch (Exception ex)
        {
            Console.WriteLine("ERROR: " + ex);
        }
    }
}
