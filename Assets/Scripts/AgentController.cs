// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;
using System.Linq;


[Serializable]
public class PosData
{
    public string id;
    public float x, y, z;

    public PosData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class TrafficLightData : PosData
{
    public string state;
    public string axis;
    public string direction;

    public TrafficLightData(string id, float x, float y, float z, string state, string axis, string direction)
        : base(id, x, y, z) // Calls the constructor of PosData
    {
        this.state = state;
        this.axis = axis;
        this.direction = direction;
    }
}

[Serializable]
public class SimulationData
{
    public List<PosData> destinationPos;
    public List<PosData> obstaclePos;
    public List<PosData> roadPos;
    public List<TrafficLightData> trafficLightPos;

    public List<PosData> carPos;
}

public class AgentController : MonoBehaviour
{
    string serverUrl = "http://localhost:8585";
    string getDataEP = "/getAgents";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    public SimulationData simulationData;
    bool updated = false;

    public GameObject carPrefab, obstaclePrefab, floor, trafficLightPrefab, roadPrefab, destinationPrefab;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    public Texture[] buildingTextures; // Assign this array in the inspector with your textures
    private int simulationUpdateCounter = 0; // Counter for simulation updates
    private bool trafficLightsOriented = false; // Ensures traffic lights are only oriented once
    Dictionary<string, GameObject> cars = new Dictionary<string, GameObject>();
    Dictionary<string, GameObject> trafficLights = new Dictionary<string, GameObject>();

    void Start()
    {
        // Initializes
        simulationData = new SimulationData();
        // Init the car dictionary
        cars = new Dictionary<string, GameObject>();
        trafficLights = new Dictionary<string, GameObject>();

        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {
        if (timer <= 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
            foreach (PosData carPos in simulationData.carPos)
            {
                GameObject car = GameObject.Find(carPos.id);
                CarMovement carMovement = car.GetComponent<CarMovement>();
                carMovement.SetTarget(new Vector3(carPos.x, carPos.y, carPos.z));
            }
        }
        else
        {
            timer -= Time.deltaTime;
        }

        if (updated)
        {
            dt = 1.0f - (timer / timeToUpdate);
            dt = Mathf.Clamp(dt, 0.0f, 1.0f);
            foreach (PosData carPos in simulationData.carPos)
            {
                GameObject car = GameObject.Find(carPos.id);
                CarMovement carMovement = car.GetComponent<CarMovement>();
                carMovement.Move(dt);
            }
        }
    }

    // City generation methods
    float GetRandomHeight()
    {
        // Replace min and max with your desired range
        float minHeight = 2.0f; // Minimum height
        float maxHeight = 5.0f; // Maximum height
        return UnityEngine.Random.Range(minHeight, maxHeight);
    }
    private void AssignRandomTexture(GameObject building)
    {
        if (buildingTextures.Length > 0)
        {
            // Specify UnityEngine.Random to resolve the ambiguity
            Texture selectedTexture = buildingTextures[UnityEngine.Random.Range(0, buildingTextures.Length)];
            Renderer renderer = building.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.material.mainTexture = selectedTexture;
            }
            else
            {
                Debug.LogWarning("Renderer not found on building object");
            }
        }
    }

    // Server communication methods
    IEnumerator SendConfiguration()
    {
        /*
        The SendConfiguration method is used to send the configuration to the server.
        */

        UnityWebRequest www = UnityWebRequest.PostWwwForm(serverUrl + sendConfigEndpoint, "");
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            // Once the configuration has been sent, it launches a coroutine to get the agents data.
            StartCoroutine(GetData(true));
        }
    }

    IEnumerator GetData(bool firstTime)
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getDataEP);
        yield return www.SendWebRequest();
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
            updated = false;
        }
        else
        {
            if (www.downloadHandler.text == null)
            {
                Debug.LogError("www.downloadHandler.text is null");
                yield break; // Stop the coroutine if data is null
            }

            simulationData = JsonUtility.FromJson<SimulationData>(www.downloadHandler.text);

            if (simulationData == null)
            {
                Debug.LogError("Failed to parse SimulationData from JSON.");
                updated = false;
                yield break; // Stop the coroutine if data is null
            }

            if (firstTime)
            {
                InitializeSimulation();
            }
            else
            {
                UpdateSimulationFromData();
            }
            updated = true;
        }
    }

    private void UpdateSimulationFromData()
    {
        // This block will run only once at mesa step 1
        if (simulationUpdateCounter == 1 && !trafficLightsOriented)
        {
            foreach (TrafficLightData trafficLightPos in simulationData.trafficLightPos)
            {
                if (trafficLights.ContainsKey(trafficLightPos.id))
                {
                    GameObject trafficLight = trafficLights[trafficLightPos.id];
                    if (trafficLight != null)
                    {
                        // Rotate the traffic light if necessary
                        if (trafficLightPos.direction == "Left" && trafficLightPos.axis == "x" ||
                            trafficLightPos.direction == "Up" && trafficLightPos.axis == "y")
                        {
                            trafficLight.transform.Rotate(0, 180, 0);
                        }
                    }
                }
            }
            trafficLightsOriented = true; // Set this flag to true to prevent re-execution
        }

        // Regular update
        foreach (TrafficLightData trafficLightPos in simulationData.trafficLightPos)
        {
            if (!trafficLights.ContainsKey(trafficLightPos.id))
            {
                Debug.LogError("Traffic light not found: " + trafficLightPos.id);
                continue;
            }

            GameObject trafficLight = trafficLights[trafficLightPos.id];
            if (trafficLight != null)
            {
                TrafficLightController trafficLightController = trafficLight.GetComponentInChildren<TrafficLightController>();
                if (trafficLightController != null)
                {
                    trafficLightController.SetState(trafficLightPos.state);
                }
                else
                {
                    Debug.LogError("TrafficLightController component not found on traffic light: " + trafficLightPos.id);
                }
            }
            else
            {
                Debug.LogError("Traffic light GameObject is null for ID: " + trafficLightPos.id);
            }
        }

        // First, ensure all cars in simulationData.carPos are created or found
        foreach (PosData carPos in simulationData.carPos)
        {
            GameObject car = GameObject.Find(carPos.id);
            if (car == null)
            {
                car = Instantiate(carPrefab, new Vector3(0, 0, 0), Quaternion.identity);
                car.name = carPos.id;
                cars.Add(carPos.id, car);
            }
        }

        // Next, check and remove any cars that are not in simulationData.carPos
        List<string> carIdsToRemove = new List<string>();
        foreach (KeyValuePair<string, GameObject> carEntry in cars)
        {
            if (!simulationData.carPos.Any(posData => posData.id == carEntry.Key))
            {
                carIdsToRemove.Add(carEntry.Key);
            }
        }

        foreach (string carId in carIdsToRemove)
        {
            GameObject car = cars[carId];
            CarMovement carMovement = car.GetComponent<CarMovement>();
            List<GameObject> wheels = carMovement.GetWheelObjects();
            foreach (GameObject wheel in wheels)
            {
                Destroy(wheel);
            }
            cars.Remove(carId);
            Destroy(car);
        }
        simulationUpdateCounter++;
    }

    private void InitializeSimulation()
    {
        foreach (PosData destinationPos in simulationData.destinationPos)
        {
            GameObject destination = Instantiate(destinationPrefab, new Vector3(destinationPos.x, destinationPos.y, destinationPos.z), Quaternion.identity); ;
        }
        foreach (PosData obstaclePos in simulationData.obstaclePos)
        {
            GameObject obstacle = Instantiate(obstaclePrefab, new Vector3(obstaclePos.x, obstaclePos.y, obstaclePos.z), Quaternion.identity);
            AssignRandomTexture(obstacle); // Assign a random texture to the building
                                           // Apply random height
            float randomHeight = GetRandomHeight();
            Vector3 currentScale = obstacle.transform.localScale;
            obstacle.transform.localScale = new Vector3(currentScale.x, randomHeight, currentScale.z);
        }
        foreach (PosData roadPos in simulationData.roadPos)
        {
            GameObject road = Instantiate(roadPrefab, new Vector3(roadPos.x, roadPos.y, roadPos.z), Quaternion.identity); ;
        }
        foreach (TrafficLightData trafficLightPos in simulationData.trafficLightPos)
        {
            string axis = trafficLightPos.axis;

            GameObject trafficLight = Instantiate(
                trafficLightPrefab,
                new Vector3(
                    trafficLightPos.x,
                    trafficLightPos.y,
                    trafficLightPos.z
                    ),
                Quaternion.identity
                );

            trafficLight.name = trafficLightPos.id;

            // // Check if the axis is "y" and rotate accordingly
            if (axis == "y")
            {
                // Since they initially face -x, we rotate them 90 degrees around the y-axis to face +z
                trafficLight.transform.Rotate(0, 90, 0);
            }

            trafficLights.Add(trafficLightPos.id, trafficLight);

            // and a road
            GameObject road = Instantiate(roadPrefab, new Vector3(trafficLightPos.x, trafficLightPos.y, trafficLightPos.z), Quaternion.identity);
        }
    }

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
            StartCoroutine(GetData(false));
    }
}