# Introduction

Write ipywidgets like React. Create a Web-based UI from Python, using ipywidgets made easier, fun, and without bugs.

## What is Reacton

A way to write reusable components in a React-like way, to make Python-based UI's using the ipywidgets ecosystem (ipywidgets, ipyvolume, bqplot, threejs, leaflet, ipyvuetify, ...).

## Why? What is the problem?

Non-declarative UI's are complex: You have to attach and detach event handlers at the right point, there are many possibles states your UI can be in, and moving from one state to the other can be very hard to do manually and is very error-prone.

Using Reacton, you write a component that gives a declarative description of the UI you want based on data. If the data changes, your component render function re-executes, and Reacton will find out how to go from the previous state to the new state. No more manual "diffing" on the UI, no more manual tracking of which event handlers to attach and detach.

A common issue we also see is that there is one piece of code to set up the UI, and scattered around in many event handlers the changes that are almost repetitions of the initialization code.

## Why use a React-like solution

Using a declarative way, in a React (JS) style, makes your codebase smaller, less error-prone, and easier to reason about. We don't see a good reason *not* to use it.

Also, React has proven itself, and by adopting a proven technology, we can stand on the shoulders of giants, make use of a lot of existing resources, and do not have to reinvent the wheel.

## What does Reacton do for me?

Instead of telling ipywidgets what to do, e.g.:

  * Responding to events.
  * Changing properties.
  * Attaching and detaching event handlers.
  * Adding and removing children.
  * Manage widget lifetimes (creating and destroying).

You tell Reacton what you want (which Widgets you want to have), and you let Reacton take care of the above.
