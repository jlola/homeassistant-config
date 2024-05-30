using System.Security.Cryptography.X509Certificates;
using NetDaemon.HassModel.Entities;
using NetDaemon.Extensions;
using HomeAssistantGenerated;

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
        
        #endregion

        #region  Properties

        private ILogger<PoolPumpController> logger;
        private bool firstRun;
        public SwitchEntity PoolPumpSwitchEntity { get; set; }
        public BinarySensorEntity PoolPumpButtonEntity { get; set; }

        public NumericSensorEntity SensorTemperatureSolarPanel { get; set; }

        #endregion
    
        #region Constructor

        public PoolPumpController(IHaContext ha, ILogger<PoolPumpController> logger)
        {            
            this.logger = logger ?? throw new ArgumentNullException(nameof(logger));
            var entities = new Entities(ha);
            this.firstRun = true;
            this.PoolPumpSwitchEntity = entities.Switch.Switch77PoolPump;
            this.PoolPumpButtonEntity = entities.BinarySensor.BinarySensor71PoolPumpButton;
            this.SensorTemperatureSolarPanel = entities.Sensor.TempSolarHeater;

            this.PoolPumpButtonEntity.StateChanges().Subscribe(OnPoolPumpButton);
            this.SensorTemperatureSolarPanel.StateChanges().Subscribe(OnSensorTemperatureSolarPanelChange);
            this.logger.LogInformation("PoolPumpController started");
        }

        #endregion

        public void OnSensorTemperatureSolarPanelChange(StateChange state)
        {
            this.logger.LogInformation("OnSensorTemperatureSolarPanelChange callback {0} state: {1}, first run: {2}"
                , SensorTemperatureSolarPanel.EntityId, SensorTemperatureSolarPanel.State, this.firstRun);

            Double.TryParse(state.Old?.State, out var oldValue);
            Double.TryParse(state.New?.State, out var solarPanelTemperature);
            
            logger.LogInformation($"temperature solar panel old: {oldValue} new: {solarPanelTemperature}");

            if (solarPanelTemperature > 45.0)
                PoolPumpSwitchEntity.TurnOn();
            else
                PoolPumpSwitchEntity.TurnOff();        
        }

        public void OnPoolPumpButton(StateChange state)
        {            
            var switchStateOn = PoolPumpSwitchEntity.IsOn();
            this.logger.LogInformation("pool button callback {0} state: {1}, first run: {2}", PoolPumpButtonEntity.EntityId, PoolPumpSwitchEntity.State, this.firstRun);
            
            if (!firstRun)
            {
                if (this.PoolPumpSwitchEntity.IsOn())
                    PoolPumpSwitchEntity.TurnOff();
                else
                    PoolPumpSwitchEntity.TurnOn();
            }
            else
            {
                firstRun = false;
                PoolPumpSwitchEntity.TurnOff();
            }
            
            
            this.firstRun = false;
        }        
    }
}