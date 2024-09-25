// Use unique namespaces for your apps if you going to share with others to avoid
// conflicting names

namespace HassModel;

// /// <summary>
// ///     Hello world showcase using the new HassModel API
// /// </summary>
// [NetDaemonApp]
// public class HelloWorldApp
// {
//     public HelloWorldApp(IHaContext ha, ILogger<HelloWorldApp> logger)
//     {        
//         logger.LogTrace("This is at Verbose level");
//             logger.LogDebug("This is at Debug level");
//             logger.LogInformation("This is at Information level");
//             logger.LogWarning("This is at Warning level");
//             logger.LogError("This is at Error level");
//             logger.LogCritical("This is at Fatal level");

//         ha.CallService("notify", "persistent_notification", data: new {message = "Notify me", title = "Hello world!"});        
//     }
// }