using System.Collections;
using System.Reflection;
using NUnit.Framework;
using Platformer.Core;
using Platformer.Mechanics;
using UnityEngine;
using UnityEngine.TestTools;

public class PlayerHealthTests
{
    private GameObject player;
    private Health health;

    [SetUp]
    public void SetUp()
    {
        player = new GameObject("TestPlayer");
        player.SetActive(false);
        health = player.AddComponent<Health>();
        health.maxHP = 3;
        player.SetActive(true);
    }

    [UnityTearDown]
    public IEnumerator TearDown()
    {
        // Health schedules HealthIsZero when it reaches zero.
        Simulation.Clear();
        Object.Destroy(player);
        yield return null;
    }

    [UnityTest]
    public IEnumerator PlayMode_PlayerTakesDamage_HealthDecreases()
    {
        Assert.That(health.IsAlive, Is.True);

        health.Decrement();
        Assert.That(health.IsAlive, Is.True, "Player must survive the first hit.");

        health.Decrement();
        Assert.That(health.IsAlive, Is.True, "Player must survive the second hit.");

        health.Decrement();
        Assert.That(health.IsAlive, Is.False, "Player must die after three hits.");
        yield break;
    }

    [UnityTest]
    public IEnumerator PlayMode_Variant3_Die_SetsHealthToZero()
    {
        var currentHP = typeof(Health).GetField("currentHP", BindingFlags.Instance | BindingFlags.NonPublic);
        Assert.That(currentHP, Is.Not.Null, "Health must expose its current HP to this test via reflection.");
        Assert.That(currentHP.GetValue(health), Is.EqualTo(3));
        Assert.That(health.IsAlive, Is.True);

        health.Die();

        Assert.That(currentHP.GetValue(health), Is.EqualTo(0));
        Assert.That(health.IsAlive, Is.False);
        yield break;
    }
}
