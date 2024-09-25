using System.Security.Cryptography.X509Certificates;
using NetDaemon.HassModel.Entities;
using NetDaemon.Extensions;
using HomeAssistantGenerated;
using System.Runtime.InteropServices;

namespace HassModel.HomeApps.Controllers
{
    public class EntityStateExt
    {
        public const string STATE_UNAVAILABLE = "unavailable";
        public static bool IsUnavailable(EntityState entityState)
        {
            if (entityState == null || entityState.State == STATE_UNAVAILABLE)
                return true;

            return false;
        }
    }
}