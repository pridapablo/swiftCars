/* 
    Building texture randomizer script.

    Authors:
            Pablo Banzo Prida
            María Fernanda Cortés Lozano

        Date: 30/11/2023
*/

using UnityEngine;

public class RandomBuildingTexture : MonoBehaviour
{
    public Texture[] textures; // Texture array for the building textures
    void Start()
    {
        if (textures.Length > 0)
        {
            Texture selectedTexture = textures[Random.Range(0, textures.Length)];
            GetComponent<Renderer>().material.mainTexture = selectedTexture;
        }
    }
}
