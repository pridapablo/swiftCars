/* 
Tarea CG 2
This code uses the transformation matrices to move the car and its wheels.

Created by Fer Cortés
*/

// import libraries
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class MatrixMovement : MonoBehaviour
{
    // adds a header to the inspector for the car variables
    [Header ("Car Movement")]
    [SerializeField] Vector3 displacement; 
    [SerializeField] float carScale; 

    [Header ("Wheels")] // adds a header to the inspector for the wheel variables
    [SerializeField] Vector3 wheelScale;
    [SerializeField] GameObject wheelPrefab; // adds a field to the inspector for the wheel prefab, 
    //the wheel is the one created on the previos homework.
    [SerializeField] List<Vector3> wheels; // position of the wheels


    [Header ("Movement Interpolation")]
    [SerializeField] Vector3 StartPos; // adds a field to the inspector for the start position
    [SerializeField] Vector3 StopPos; // adds a field to the inspector for the stop position
    [SerializeField] float MotionTime; 
    [SerializeField] List<Vector3> Waypoints;
    
    Mesh mesh; // creates a mesh variable
    Vector3[] oldVertices; // creates a vector3 array for the base vertices
    Vector3[] newVertices; // creates a vector3 array for the new vertices
    List<Mesh> wheelMesh; // creates a list of meshes for the wheels
    List<Vector3[]> oldWheelVertices; // creates a list of vector3 arrays for the starting vertices of the wheels
    List<Vector3[]> newWheelVertices; // creates a list of vector3 arrays for the new vertices of the wheels

    private List<GameObject> wheelObjects = new List<GameObject>(); // creates a list of game objects for the wheels

    void Start() 
    {
        mesh = GetComponentInChildren<MeshFilter>().mesh; // gets the mesh component of the car
        oldVertices = mesh.vertices; // gets the vertices of the mesh and stores it in the oldVertices array
        newVertices = new Vector3[oldVertices.Length]; // creates a new array for the new vertices
        wheelMesh = new List<Mesh>(); // creates a new list of meshes for the wheels
        oldWheelVertices = new List<Vector3[]>(); 
        newWheelVertices = new List<Vector3[]>();

        foreach (Vector3 wheelPos in wheels){
            GameObject wheel = Instantiate(wheelPrefab, new Vector3(0,0,0), Quaternion.identity); // instantiates the wheel prefab
            wheelObjects.Add(wheel); // adds the wheel to the list of wheel objects
        }

        // for each wheel object, it gets the mesh component and stores it in the wheelMesh list
        for (int i = 0; i < wheelObjects.Count; i++){ 
            wheelMesh.Add(wheelObjects[i].GetComponentInChildren<MeshFilter>().mesh);
            oldWheelVertices.Add(wheelMesh[i].vertices);
            newWheelVertices.Add(new Vector3[oldWheelVertices[i].Length]);
        }
    }

    void Update() {
        Matrix4x4 carMatrix = Car(); // gets the car matrix
        DoTransformCar(carMatrix); // transforms the car
        for (int i = 0; i < wheelObjects.Count; i++) { // for each wheel, it gets the wheel matrix and transforms it
            DoTransformWheels(Wheel(carMatrix, i), i);
        }
}

    // creates a matrix for the car
    Matrix4x4 Car(){
        Matrix4x4 moveObject = HW_Transforms.TranslationMat(displacement.x*Time.time,
                                                    displacement.y*Time.time,
                                                    displacement.z*Time.time);
        if (displacement.x != 0){
            float angle = Mathf.Atan2(displacement.x, displacement.z) * Mathf.Rad2Deg;
            Matrix4x4 rotate = HW_Transforms.RotateMat(angle, AXIS.Y);
            Matrix4x4 composite = moveObject * rotate;
            return composite;
        } 
        else {
            Matrix4x4 composite = moveObject;
            return composite;
        }
    }

// creates a matrix for the wheels
    Matrix4x4 Wheel(Matrix4x4 carComposite, int wheelIndex){
        Matrix4x4 scale = HW_Transforms.ScaleMat(wheelScale.x, wheelScale.y, wheelScale.z); // scales the wheels
        Matrix4x4 initialRotate = HW_Transforms.RotateMat(90, AXIS.Y); // rotates the wheels when they appear 
        Matrix4x4 rotate = HW_Transforms.RotateMat(-90 * Time.time, AXIS.X); 
        Matrix4x4 move = HW_Transforms.TranslationMat(wheels[wheelIndex].x, wheels[wheelIndex].y, wheels[wheelIndex].z);
        Matrix4x4 composite = carComposite * move * rotate * initialRotate * scale;
        return composite;
    }

// car transformation
    void DoTransformCar(Matrix4x4 carComposite) 
    {
        for (int i = 0; i < newVertices.Length; i++) 
        {
            Vector4 temp = new Vector4(oldVertices[i].x,
                                    oldVertices[i].y,
                                    oldVertices[i].z,
                                    1);
            newVertices[i] = carComposite * temp;
        }
        mesh.vertices = newVertices;
        mesh.RecalculateNormals();
    }

// wheel transformation
    void DoTransformWheels(Matrix4x4 wheelComposite, int wheelIndex){
        for (int j = 0; j < newWheelVertices[wheelIndex].Length; j++)
        {
            Vector4 temp = new Vector4(oldWheelVertices[wheelIndex][j].x,
                                        oldWheelVertices[wheelIndex][j].y,
                                        oldWheelVertices[wheelIndex][j].z,
                                        1);
            newWheelVertices[wheelIndex][j] = wheelComposite * temp;
        }

        wheelMesh[wheelIndex].vertices = newWheelVertices[wheelIndex];
        wheelMesh[wheelIndex].RecalculateNormals();
    }
}
