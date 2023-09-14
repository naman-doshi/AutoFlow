using System.Collections.Generic;
using UnityEngine;

public class TrafficSystem : MonoBehaviour
{
    public float segDetectThresh = 0.1f;

    public List<Segment> segments;
    public List<Intersection> intersections;

    public GameObject segmentContainer;
    public GameObject intersectionContainer;

    public GameObject segmentPrefab;
    public GameObject intersectionPrefab;

    public void Reset()
    {
        segmentContainer = transform.Find("Segments").gameObject;
        intersectionContainer = transform.Find("Intersections").gameObject;

        segments = new List<Segment>(segmentContainer.GetComponentsInChildren<Segment>());
        intersections = new List<Intersection>(intersectionContainer.GetComponentsInChildren<Intersection>());
    }

    public List<Node> GetAllNodes()
    {
        var nodes = new List<Node>();
        foreach (var seg in segments) nodes.AddRange(seg.nodes);
        return nodes;
    }
}
