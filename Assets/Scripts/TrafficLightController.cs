using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TrafficLightController : MonoBehaviour
{
    public Material greenLightMaterial;
    public Material redLightMaterial;
    private Renderer lightRenderer;

    void Start()
    {
        lightRenderer = GetComponent<Renderer>();
        if (lightRenderer == null)
        {
            Debug.LogError("No Renderer component found on " + gameObject.name);
        }
    }

    public void UpdateLight(bool isGreen)
    {
        if (lightRenderer != null)
        {
            lightRenderer.material = isGreen ? greenLightMaterial : redLightMaterial;
        }
        else
        {
            Debug.LogError("Renderer is not initialized on " + gameObject.name);
        }
    }
}
