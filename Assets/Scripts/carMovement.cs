/* 
    Manual movement of the car and wheels using matrices.
    Interpolates car movement between two points and is called by the agent controller.

    Authors:
            Pablo Banzo Prida
            María Fernanda Cortés Lozano

        Date: 30/11/2023
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CarMovement : MonoBehaviour
{
    // adds a header to the inspector for the car variables
    [Header("Car Movement")]
    [SerializeField] float carScale;

    [Header("Wheels")] // adds a header to the inspector for the wheel variables
    [SerializeField] Vector3 wheelScale;
    [SerializeField] GameObject wheelPrefab; // adds a field to the inspector for the wheel prefab, 
    //the wheel is the one created on the previos homework.
    [SerializeField] List<Vector3> wheels; // position of the wheels
    Mesh mesh; // creates a mesh variable
    Vector3[] oldVertices; // creates a vector3 array for the base vertices
    Vector3[] newVertices; // creates a vector3 array for the new vertices
    List<Mesh> wheelMesh; // creates a list of meshes for the wheels
    List<Vector3[]> oldWheelVertices; // creates a list of vector3 arrays for the starting vertices of the wheels
    List<Vector3[]> newWheelVertices; // creates a list of vector3 arrays for the new vertices of the wheels

    private Vector3 current = new Vector3(0, 0, 0); // current position of the car
    private Vector3 target = new Vector3(0, 0, 0); // target of the car
    private Vector3 previous = new Vector3(0, 0, 0); // previous position of the car

    private List<GameObject> wheelObjects = new List<GameObject>(); // creates a list of game objects for the wheels

    public List<GameObject> GetWheelObjects() // returns the list of wheel objects
    {
        return wheelObjects;
    }

    void Start()
    {
        mesh = GetComponentInChildren<MeshFilter>().mesh; // gets the mesh component of the car
        oldVertices = mesh.vertices; // gets the vertices of the mesh and stores it in the oldVertices array
        newVertices = new Vector3[oldVertices.Length]; // creates a new array for the new vertices
        wheelMesh = new List<Mesh>(); // creates a new list of meshes for the wheels
        oldWheelVertices = new List<Vector3[]>();
        newWheelVertices = new List<Vector3[]>();

        foreach (Vector3 wheelPos in wheels)
        {
            GameObject wheel = Instantiate(wheelPrefab, new Vector3(0, 0, 0), Quaternion.identity); // instantiates the wheel prefab
            wheelObjects.Add(wheel); // adds the wheel to the list of wheel objects
        }

        // for each wheel object, it gets the mesh component and stores it in the wheelMesh list
        for (int i = 0; i < wheelObjects.Count; i++)
        {
            wheelMesh.Add(wheelObjects[i].GetComponentInChildren<MeshFilter>().mesh);
            oldWheelVertices.Add(wheelMesh[i].vertices);
            newWheelVertices.Add(new Vector3[oldWheelVertices[i].Length]);
        }
    }

    public void SetTarget(Vector3 newTarget)
    {
        if (newTarget == this.target) // If the new target is the same as the current or the target is the same as the current
        {
            previous = this.current;
        }
        current = this.target; // Update current since we are moving from current to new target
        this.target = newTarget; // Set new target
    }

    public void Move(float dt)
    {
        // Interpolate position based on dt
        Vector3 interpolatedPosition = Vector3.Lerp(current, target, dt);

        if (current == Vector3.zero) // If current is zero, we just placed the car
        {
            interpolatedPosition = target;
        }

        Matrix4x4 carMatrix = Car(interpolatedPosition);
        DoTransformCar(carMatrix);

        for (int i = 0; i < wheelObjects.Count; i++)
        {
            Matrix4x4 wheelMatrix = Wheel(carMatrix, i);
            DoTransformWheels(wheelMatrix, i);
        }
    }

    // creates a composite matrix for the car
    Matrix4x4 Car(Vector3 interpolatedPosition)
    {
        Matrix4x4 moveObject = HW_Transforms.TranslationMat(interpolatedPosition.x,
                                                            interpolatedPosition.y,
                                                            interpolatedPosition.z);

        Matrix4x4 scale = HW_Transforms.ScaleMat(carScale, carScale, carScale);
        float angle = Mathf.Atan2(target.x - current.x, current.z - target.z) * Mathf.Rad2Deg;

        if (current == target) // If current is equal to target, we are not moving
        {
            angle = Mathf.Atan2(previous.x, previous.z) * Mathf.Rad2Deg;
        }

        angle += 180; // Offset rotation

        Matrix4x4 rotate = HW_Transforms.RotateMat(angle, AXIS.Y);
        Matrix4x4 composite = moveObject * rotate * scale;
        return composite;
    }

    // creates a composite matrix for the wheels
    Matrix4x4 Wheel(Matrix4x4 carComposite, int wheelIndex)
    {
        Matrix4x4 scale = HW_Transforms.ScaleMat(wheelScale.x, wheelScale.y, wheelScale.z); // scales the wheels
        Matrix4x4 initialRotate = HW_Transforms.RotateMat(90, AXIS.Y); // rotates the wheels when they appear 
        Matrix4x4 rotate = HW_Transforms.RotateMat(-90 * Time.time, AXIS.X);
        Matrix4x4 move = HW_Transforms.TranslationMat(wheels[wheelIndex].x, wheels[wheelIndex].y, wheels[wheelIndex].z);
        Matrix4x4 composite = carComposite * move * rotate * initialRotate * scale;
        return composite;
    }

    // car transformation (mesh update)
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

    // wheel transformation (mesh update)
    void DoTransformWheels(Matrix4x4 wheelComposite, int wheelIndex)
    {
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
