using System.Collections.Generic;
using UnityEngine;

public class Segment : MonoBehaviour
{
    public List<Segment> nextSegments;
    [HideInInspector] public List<Node> nodes;
    [HideInInspector] public TrafficSystem system;

    private int _id;

    public int Id
    {
        get => _id;
        set
        {
            _id = value;
            name = "Segment" + _id;
        }
    }

    public void Reset()
    {
        tag = "Segment";
    }

    public bool IsOnSegment(Vector3 point)
    {
        for (var i = 0; i < nodes.Count; i++)
        {
            var d1 = Vector3.Distance(nodes[i].transform.position, point);
            var d2 = Vector3.Distance(nodes[i + 1].transform.position, point);
            var d3 = Vector3.Distance(nodes[i].transform.position, nodes[i + 1].transform.position);
            var a = d1 + d2 - d3;
            if (a < system.segDetectThresh && a > -system.segDetectThresh)
                return true;
        }

        return false;
    }
}
