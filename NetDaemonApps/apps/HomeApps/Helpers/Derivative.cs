
public struct TimeValue
{
    public TimeValue(DateTime time, decimal val)
    {
        this.Value = val;
        this.Time = time;
    }
    public decimal Value{ get; set; }
    public DateTime Time { get; set; }
}

public class Derivative
{
    private TimeValue? xkminus1;
    private TimeValue? xkplus1;

    private TimeValue? xk;

    public Derivative()
    {        
    }

    public void AddNewValue(DateTime time,decimal val)
    {
        xkminus1 = xk;
        xk = xkplus1;
        xkminus1 = new TimeValue(time, val);
    }

    public double GetDerivative()
    {
        
    }
}