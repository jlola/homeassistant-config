// Use unique namespaces for your apps if you going to share with others to avoid
// conflicting names

using NetDaemon.HassModel.Entities;

namespace HassModel;

/// <summary>
///     Hello world showcase using the new HassModel API
/// </summary>
[NetDaemonApp]
public class HelloWorldApp
{
    public HelloWorldApp(IHaContext ha, ILogger<HelloWorldApp> logger)
    {
        logger.LogError("Error in constructor");
        ha.CallService("notify", "persistent_notification", data: new {message = "Notify me", title = "Hello world!"});        
    }
}