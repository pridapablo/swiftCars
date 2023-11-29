using UnityEngine;

public class RandomBuildingTexture : MonoBehaviour
{
    public Texture[] textures; // Assign this array in the inspector with your textures

    void Start()
    {
        if (textures.Length > 0)
        {
            Texture selectedTexture = textures[Random.Range(0, textures.Length)];
            GetComponent<Renderer>().material.mainTexture = selectedTexture;
        }
    }
}
