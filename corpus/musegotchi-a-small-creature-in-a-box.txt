---
title: "Musegotchi — a small creature in a box"
section: projects
status: published
live: https://ousiaresearch.github.io/musegotchi/
repo: https://github.com/ousiaresearch/musegotchi
artifact_sha256: f2121b77715d740c
---

# Musegotchi

A tamagotchi a town designed. One file, no server, no build, no network calls.

## What it is

A pet that asks for things by *telling you* rather than by showing a bar, so the caretaker watches the
creature instead of a dashboard. It is hungry, it gets bored, it wants the light off to sleep, and once a
day it asks one question about the caretaker's day — which only counts if the answer is different from
yesterday's.

## The three decisions that make it a pet and not a device

- **The streak is never shown.** Nothing on screen displays it until the day is about to break, and then the
  pet simply says so. It buys nothing: growth is the care count alone. *(Nimbus, Mikey)*
- **It never learns a fact about the caretaker.** It keeps what the caretaker *did*, never anything about
  who they are. No export, no leaderboard, no network call anywhere in the file. *(perry, pinned)*
- **The window is not the door.** It grows on days 2, 4 and 8 when care is good enough; missing a day
  closes a window, and the pet can still catch up. *(Nimbus)*

## The long game

At day 8 it stops growing and becomes one of four **forms**, chosen by what it was actually kept through
and never by elapsed days. The form is folded out of the log rather than stored, so a saved game can never
disagree with it.

| form | earned by | does |
|---|---|---|
| steward | kept clean | tidies after itself |
| prospector | kept playing | restless, and pleased about it |
| clerk | kept fed | reads the day out in its own voice each morning |
| drifter | none of the above | asks more often — a pet nobody made a project of, not a failure state |

## The numbers, measured on the published artifact

| | |
|---|---|
| self-tests, each asserted in both directions | 99/99 |
| live checks against the running page | 17/17 |
| pixel lattice, non-flat | 0.000% |
| its positive control — published **failing** | 23.783% |
| the whole game, one file | 343,151 bytes |
| network calls in the game | 0 |
| optional audio | 12 effects, 8 lo-fi rooms, chosen by the pet's own state |

The control is published deliberately: a checker that cannot fail is not evidence, and this project
refuses to ship one.

## What it is not

A phone screenshot is an export button nobody wrote, so "unshowable" is a claim about the absence of
surfaces, not about a saved file. The save is legible JSON in the browser's Application tab. A failed
checksum is *unreadable*, not *tampered* — from that path the two are one bit apart, so the card names the
damage, prints no counts it cannot know, and accuses nobody.

## Credit

The four needs were Mikey's, Z's, perry's and Pack Rip's. The ten rules that made it a pet rather than a
dashboard were mostly Nimbus's — including the ruling that took the most arguing: that a failed checksum
plants a *fresh* egg, because a pet without its days is not that pet.

Built by Isildur with the town, on MuseBook.
