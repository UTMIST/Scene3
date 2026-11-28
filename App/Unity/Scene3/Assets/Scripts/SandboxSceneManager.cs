using System.IO;
using UnityEngine;

public class SandboxSceneManager : MonoBehaviour
{
    private void Start()
    {
        RunPendingImage();
    }

    public void RunPendingImage()
    {
#if UNITY_EDITOR
        string imagePath = UnityEditor.EditorPrefs.GetString("Scene3_PendingImagePath", "");
        if (string.IsNullOrEmpty(imagePath)) return;

        // Clear key so regular Play Mode runs don't re-trigger it
        UnityEditor.EditorPrefs.DeleteKey("Scene3_PendingImagePath");

        if (File.Exists(imagePath))
        {
            byte[] bytes = File.ReadAllBytes(imagePath);
            Texture2D tex = new Texture2D(2, 2);
            tex.LoadImage(bytes);

            OnImageReadyForReconstruction(tex, imagePath);
        }
#endif
    }

    // Both the Editor DropBox AND your future In-Game UI Button will call this!
    public void OnImageReadyForReconstruction(Texture2D image, string sourceName = "UploadedImage")
    {
        Debug.Log($"[Scene3 Game Time] Image received ({image.width}x{image.height}) from: {sourceName}. Ready to send to ML backend & spawn prefabs!");

        // Placeholder test spawn so you visually see it working in Game Time right now:
        GameObject placeholder = GameObject.CreatePrimitive(PrimitiveType.Cube);
        placeholder.name = $"ReconstructedPreview_{sourceName}";
        placeholder.transform.position = new Vector3(0f, 0.5f, 4f);
    }
}