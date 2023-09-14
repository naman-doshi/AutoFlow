using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(TrafficSystem))]
public class TrafficSystemEditor : Editor
{
    public bool placeSegmentMode;

    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();

        var sys = (TrafficSystem)target;

        if (GUILayout.Button("Refresh")) sys.Reset();
        EditorGUILayout.Toggle("New Segment", true);
    }
}
