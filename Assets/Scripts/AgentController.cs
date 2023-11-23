﻿// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

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
    public bool isGreen;

    public TrafficLightData(string id, float x, float y, float z, bool isGreen)
        : base(id, x, y, z) // Calls the constructor of PosData
    {
        this.isGreen = isGreen;
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
    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;

    public GameObject carPrefab, obstaclePrefab, floor, trafficLightPrefab, roadPrefab, destinationPrefab;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        // Initializes
        simulationData = new SimulationData();

        // prevPositions = new Dictionary<string, Vector3>();
        // currPositions = new Dictionary<string, Vector3>();

        // agents = new Dictionary<string, GameObject>();

        // floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        // floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0, (float)height/2-0.5f);

        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {
        if (timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            // // Iterates over the agents to update their positions.
            // // The positions are interpolated between the previous and current positions.
            // foreach (var agent in currPositions)
            // {
            //     Vector3 currentPosition = agent.Value;
            //     Vector3 previousPosition = prevPositions[agent.Key];

            //     Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
            //     Vector3 direction = currentPosition - interpolated;

            //     agents[agent.Key].transform.localPosition = interpolated;
            //     if (direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            // }

            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }
    }

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
            Debug.Log(www.error);
        else
        {
            // Once the data has been received, it is stored in the CarsData variable.
            // Then, it iterates over the CarsData.positions list to update the
            // agents positions
            if (www.downloadHandler.text == null)
            {
                Debug.LogError("www.downloadHandler.text is null");
                yield break; // Stop the coroutine if data is null
            }
            else
            {
                Debug.Log("www.downloadHandler.text: " + www.downloadHandler.text);
            }

            simulationData = JsonUtility.FromJson<SimulationData>(www.downloadHandler.text);

            if (simulationData == null)
            {
                Debug.LogError("Failed to parse SimulationData from JSON.");
                yield break; // Stop the coroutine if data is null
            }

            if (firstTime)
            {
                foreach (PosData destinationPos in simulationData.destinationPos)
                {
                    GameObject destination = Instantiate(destinationPrefab, new Vector3(destinationPos.x, destinationPos.y, destinationPos.z), Quaternion.identity); ;
                }
                foreach (PosData obstaclePos in simulationData.obstaclePos)
                {
                    GameObject obstacle = Instantiate(obstaclePrefab, new Vector3(obstaclePos.x, obstaclePos.y, obstaclePos.z), Quaternion.identity); ;
                }
                foreach (PosData roadPos in simulationData.roadPos)
                {
                    GameObject road = Instantiate(roadPrefab, new Vector3(roadPos.x, roadPos.y, roadPos.z), Quaternion.identity); ;
                }
                foreach (TrafficLightData trafficLightPos in simulationData.trafficLightPos)
                {
                    GameObject trafficLight = Instantiate(trafficLightPrefab, new Vector3(trafficLightPos.x, trafficLightPos.y, trafficLightPos.z), Quaternion.identity); ;
                }
            }
            else
            {
                foreach (TrafficLightData trafficLightPos in simulationData.trafficLightPos)
                {
                    // GameObject trafficLight = GameObject.Find(trafficLightPos.id);
                    // trafficLight.GetComponent<TrafficLight>().isGreen = trafficLightPos.isGreen;
                }
                foreach (PosData carPos in simulationData.carPos)
                {
                    GameObject car = GameObject.Find(carPos.id);
                    if (car == null)
                    {
                        car = Instantiate(carPrefab, new Vector3(carPos.x, carPos.y, carPos.z), Quaternion.identity);
                        car.name = carPos.id;
                    }
                    else
                    {
                        car.transform.position = new Vector3(carPos.x, carPos.y, carPos.z);
                    }
                }

            }
        }
        updated = true;
        if (!started) started = true;
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

