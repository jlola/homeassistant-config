using System.Security.Cryptography.X509Certificates;
using NetDaemon.HassModel.Entities;
using NetDaemon.Extensions;

namespace HassModel.HomeApps.Controllers
{
    [NetDaemonApp]
    public class PoolPumpController
    {

        #region Constants

        public const string SOLARPUMP_MODE_ON = "On";
        public const string SOLARPUMP_MODE_OFF = "Off";
        public const string SOLARPUMP_MODE_AUTO = "Auto";
        public const string SOLARPUMP_MODE_SWIMMING = "Swimming";

        public const string pool_pump_switch = "switch.switch_7_7_pool_pump";
        public const string pool_pump_button = "binary_input.binary_sensor_7_1_pool_pump_button";
        public const string set_temperature_pump_turn_on = "";
        public const string set_temperature_pump_turn_off = "";
        public const string temperature_solar_panel_id = "sensor.temp_solar_heater";
        public const string poolpump_mode = "input_select.solar_pump_mode";

        #endregion

        private ILogger<PoolPumpController> logger;

        private bool firstRun;

        public Entity PumpSwitchEntity { get; set; }
        public Entity PoolPumpButtonEntity { get; set; }

        public Entity SensorTemperatureSolarPanel { get; set; }
    
        public PoolPumpController(IHaContext ha, ILogger<PoolPumpController> logger)
        {            
            this.logger = logger ?? throw new ArgumentNullException(nameof(logger));
            this.firstRun = true;
            PumpSwitchEntity = ha.Entity(pool_pump_switch);
            PoolPumpButtonEntity = ha.Entity(pool_pump_button);
            SensorTemperatureSolarPanel = ha.Entity(temperature_solar_panel_id);

            PoolPumpButtonEntity.StateChanges().Subscribe(OnPoolPumpButton);
            SensorTemperatureSolarPanel.StateChanges().Subscribe(OnSensorTemperatureSolarPanelChange);
            logger.LogInformation("PoolPumpController started");
        }

        public void OnSensorTemperatureSolarPanelChange(StateChange state)
        {
            logger.LogInformation("OnSensorTemperatureSolarPanelChange callback {0} state: {1}, first run: {2}"
                , SensorTemperatureSolarPanel.EntityId, SensorTemperatureSolarPanel.State, this.firstRun);
        }

        public void OnPoolPumpButton(StateChange state)
        {
            var switchStateOn = PumpSwitchEntity.IsOn();
            logger.LogInformation("pool button callback {0} state: {1}, first run: {2}", PoolPumpButtonEntity.EntityId, PumpSwitchEntity.State, this.firstRun);
            this.firstRun = false;
        }
    }
}