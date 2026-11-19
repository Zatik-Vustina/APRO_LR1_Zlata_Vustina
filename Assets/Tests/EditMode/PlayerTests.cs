using System.Linq;
using NUnit.Framework;
using Platformer.Mechanics;
using UnityEditor.SceneManagement;
using UnityEngine;

public class PlayerTests
{
    private const string MainScenePath = "Assets/Scenes/SampleScene.unity";

    [Test]
    public void EditMode_PlayerTag_IsCorrect()
    {
        var scene = EditorSceneManager.OpenPreviewScene(MainScenePath);
        try
        {
            Assert.That(scene.IsValid(), Is.True, "SampleScene must open in edit mode.");
            var players = scene.GetRootGameObjects()
                .SelectMany(root => root.GetComponentsInChildren<Transform>(true))
                .Where(candidate => candidate.name == "Player")
                .ToArray();

            Assert.That(players, Has.Length.EqualTo(1), "SampleScene must contain exactly one object named Player.");
            var player = players[0].gameObject;
            Assert.That(player.CompareTag("Player"), Is.True);
            Assert.That(player.GetComponent<PlayerController>(), Is.Not.Null);
            Assert.That(player.GetComponent<Health>(), Is.Not.Null);
        }
        finally
        {
            if (scene.IsValid())
                EditorSceneManager.ClosePreviewScene(scene);
        }
    }
}
