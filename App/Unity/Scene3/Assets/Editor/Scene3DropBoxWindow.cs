using System.IO;
using UnityEditor;
using UnityEngine;

public class Scene3DropBoxWindow : EditorWindow
{
    private Texture2D _droppedImage;
    private string _imagePath;

    // Adds a menu item at the top of Unity: Scene3 -> DropBox Window
    [MenuItem("Scene3/DropBox Window")]
    public static void ShowWindow()
    {
        GetWindow<Scene3DropBoxWindow>("Scene3 DropBox");
    }

    private void OnGUI()
    {
        GUILayout.Space(10);
        EditorGUILayout.LabelField("Scene3 Image Uploader", EditorStyles.boldLabel);

        // 1. Built-in Unity ObjectField (drag from Assets/ or click circle picker)
        EditorGUI.BeginChangeCheck();
        _droppedImage = (Texture2D)EditorGUILayout.ObjectField(
            "Project Image", _droppedImage, typeof(Texture2D), false);
        if (EditorGUI.EndChangeCheck() && _droppedImage != null)
        {
            _imagePath = AssetDatabase.GetAssetPath(_droppedImage);
        }

        GUILayout.Space(8);

        // 2. Custom Drop Box (also accepts dragging straight from Windows Explorer!)
        Rect dropRect = GUILayoutUtility.GetRect(0, 100, GUILayout.ExpandWidth(true));
        GUI.Box(dropRect, "Drag & Drop Image Here\n(From Windows Explorer or Unity Assets)");
        HandleExternalDragAndDrop(dropRect);

        // Show preview if an image is loaded
        if (_droppedImage != null)
        {
            GUILayout.Space(8);
            Rect previewRect = GUILayoutUtility.GetRect(150, 150, GUILayout.ExpandWidth(true));
            EditorGUI.DrawPreviewTexture(previewRect, _droppedImage, null, ScaleMode.ScaleToFit);
            EditorGUILayout.LabelField($"Selected: {_droppedImage.name}", EditorStyles.centeredGreyMiniLabel);
        }

        GUILayout.Space(12);

        // 3. Trigger Game-Time Reconstruction
        GUI.enabled = (_droppedImage != null);
        if (GUILayout.Button("Reconstruct in Game Time", GUILayout.Height(36)))
        {
            // Store path so Play Mode can pick it up when the scene starts
            EditorPrefs.SetString("Scene3_PendingImagePath", _imagePath);

            if (!EditorApplication.isPlaying)
                EditorApplication.isPlaying = true; // Enters Play Mode automatically
            else
                FindFirstObjectByType<SandboxSceneManager>()?.RunPendingImage();
        }
        GUI.enabled = true;
    }

    private void HandleExternalDragAndDrop(Rect dropRect)
    {
        Event evt = Event.current;
        if (!dropRect.Contains(evt.mousePosition)) return;

        if (evt.type == EventType.DragUpdated)
        {
            DragAndDrop.visualMode = DragAndDropVisualMode.Copy;
            evt.Use();
        }
        else if (evt.type == EventType.DragPerform)
        {
            DragAndDrop.AcceptDrag();

            if (DragAndDrop.objectReferences.Length > 0 && DragAndDrop.objectReferences[0] is Texture2D tex)
            {
                _droppedImage = tex;
                _imagePath = AssetDatabase.GetAssetPath(tex);
            }
            else if (DragAndDrop.paths.Length > 0)
            {
                string path = DragAndDrop.paths[0];
                byte[] bytes = File.ReadAllBytes(path);
                Texture2D loadedTex = new Texture2D(2, 2);
                if (loadedTex.LoadImage(bytes))
                {
                    loadedTex.name = Path.GetFileNameWithoutExtension(path);
                    _droppedImage = loadedTex;
                    _imagePath = path;
                }
            }
            evt.Use();
        }
    }
}