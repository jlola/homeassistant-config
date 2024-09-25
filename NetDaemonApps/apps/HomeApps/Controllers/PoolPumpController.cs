using System.Security.Cryptography.X509Certificates;
using NetDaemon.HassModel.Entities;
using NetDaemon.Extensions;
using HomeAssistantGenerated;
using System.Runtime.InteropServices;

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

        public NumericSensorEntity SensorTemperatureSolarPanelInput { get; set; }

        public InputSelectEntity PoolPumpModeSelect { get; set; }

        public InputNumberEntity MinimumSolarPanelTemperature { get; set; }

        public InputNumberEntity MaximumSolarPanelTemperature { get; set; }


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
            this.SensorTemperatureSolarPanelInput = entities.Sensor.PooltempPolltemperature;
            this.PoolPumpModeSelect = entities.InputSelect.SolarPumpMode;
            this.MinimumSolarPanelTemperature = entities.InputNumber.SolarpanelTemperatureMin;
            this.MaximumSolarPanelTemperature = entities.InputNumber.SolarpanelTemperatureMax;
            
            this.PoolPumpButtonEntity.StateChanges().Subscribe(OnPoolPumpButton);
            this.SensorTemperatureSolarPanel.StateChanges().Subscribe(OnSensorTemperatureSolarPanelChange);
            this.SensorTemperatureSolarPanelInput.StateChanges().Subscribe(OnSensorTemperatureSolarPanelInputChange);
            this.PoolPumpModeSelect.StateChanges().Subscribe(OnPoolPumpModeSelectChanged);
            this.logger.LogInformation("PoolPumpController started");
            PoolPumpSwitchEntity.TurnOff();
            ha.CallService("notify", "persistent_notification", data: new {message = "PoolPumpController started", title = "PoolPumpController"});
        }

        #endregion


        public void OnPoolPumpModeSelectChanged(StateChange state)
        {
            switch(state.New?.State)
            {
                case SOLARPUMP_MODE_SWIMMING:
                case SOLARPUMP_MODE_OFF:
                    PoolPumpSwitchEntity.TurnOff();
                    break;
                case SOLARPUMP_MODE_ON:
                    PoolPumpSwitchEntity.TurnOn();
                    break;
            }
        }

        public void OnSensorTemperatureSolarPanelInputChange(StateChange state)
        {
            if (SensorTemperatureSolarPanelInput.State==null)
            {
                this.logger.LogInformation("OnSensorTemperatureSolarPanelInputChange State is null return");
                return;
            }

            if (Double.TryParse(state.New?.State, out var solarPanelTemperatureInput))
                UpdateSolarPanelPump(SensorTemperatureSolarPanel.State, solarPanelTemperatureInput);
            else
                this.logger.LogError("OnSensorTemperatureSolarPanelChange State: {0} can't be parsed to double", state.New?.State);
        }

        public void OnSensorTemperatureSolarPanelChange(StateChange state)
        {
            if (SensorTemperatureSolarPanel.State==null)
            {
                this.logger.LogInformation("OnSensorTemperatureSolarPanelChange State is null return");
                return;
            }

            if (Double.TryParse(state.New?.State, out var solarPanelTemperature))
                UpdateSolarPanelPump(solarPanelTemperature, SensorTemperatureSolarPanelInput.State);
            else
                this.logger.LogError("OnSensorTemperatureSolarPanelChange State: {0} can't be parsed to double", state.New?.State);
        }

        private void UpdateSolarPanelPump(double? solarPanelTempOutput, double? solarPanelTempInput)
        {
            var diff = Math.Round(((decimal?)solarPanelTempOutput - (decimal?)solarPanelTempInput).GetValueOrDefault(),2);

            this.logger.LogInformation("UpdateSolarPanelPump input: {0}, output: {1}, diff: {2}, Minimum: {3}, Maximum: {4}, Pump: {5}"
                        , solarPanelTempInput, solarPanelTempOutput, diff, MinimumSolarPanelTemperature.State, MaximumSolarPanelTemperature.State, PoolPumpButtonEntity.State);

            if (PoolPumpModeSelect.EntityState?.State == SOLARPUMP_MODE_AUTO)
            {
                if (solarPanelTempOutput > MaximumSolarPanelTemperature.State && PoolPumpSwitchEntity.IsOff())
                {
                    this.logger.LogInformation("UpdateSolarPanelPump input: {0}, output: {1}, diff: {2}, Minimum: {3}, Maximum: {4}, Pump: {5}"
                        , solarPanelTempInput, solarPanelTempOutput, diff, MinimumSolarPanelTemperature.State, MaximumSolarPanelTemperature.State, "Turn ON");
                    PoolPumpSwitchEntity.TurnOn();
                }
                else if ((solarPanelTempOutput < MinimumSolarPanelTemperature.State || diff < 2) && PoolPumpSwitchEntity.IsOn())
                {
                    this.logger.LogInformation("UpdateSolarPanelPump input: {0}, output: {1}, diff: {2}, Minimum: {3}, Maximum: {4}, Pump: {5}"
                        , solarPanelTempInput, solarPanelTempOutput, diff, MinimumSolarPanelTemperature.State, MaximumSolarPanelTemperature.State, "Turn OFF");
                    PoolPumpSwitchEntity.TurnOff();
                }
            }
        }

        public void OnPoolPumpButton(StateChange state)
        {
            var switchStateOn = PoolPumpSwitchEntity.IsOn();
            this.logger.LogInformation("PoolPump Button: OnPoolPumpButton state new: {0}, state old: {1}", 
                            state.New?.State, state.Old?.State);

            if (PoolPumpButtonEntity.State==null)
            {
                this.logger.LogInformation("PoolPumpButtonEntity.State is null return");
                return;
            }
            
            if (!firstRun)
            {
                if (state.New != null && state.Old != null && state.New.State != state.Old.State && !EntityStateExt.IsUnavailable(state.New) && !EntityStateExt.IsUnavailable(state.Old))
                {
                    if (state.New.IsOff())
                    {
                        PoolPumpSwitchEntity.TurnOff();
                        PoolPumpModeSelect.SelectOption(SOLARPUMP_MODE_OFF);
                    }
                    if (state.New.IsOn())
                    {                        
                        PoolPumpModeSelect.SelectOption(SOLARPUMP_MODE_ON);
                        PoolPumpSwitchEntity.TurnOn();
                    }
                }
            }
            this.firstRun = false;
        }
    }
}