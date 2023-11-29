using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TrafficLightController : MonoBehaviour
{
    private string state;
    private Light trafficLight; // Reference to the Light component

    // Start is called before the first frame update
    void Start()
    {
        trafficLight = this.GetComponent<Light>();
    }

    public void SetState(string newState)
    {
        state = newState;
    }

    // Update is called once per frame
    void Update()
    {
        if (state == "red")
        {
            // Set the light component's color to red
            trafficLight.color = Color.red;
        }
        else
        {
            // Set the light component's color to green
            trafficLight.color = Color.green;
        }
    }
}
