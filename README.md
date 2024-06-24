# Visualizer for Queried Data during Link Traversal-based Query Processing (LTQP)

## Set-up

Clone the following repository branches: [comunica](https://github.com/RubenEschauzier/comunica/tree/feature/statistics-tracking) and [comunica-feature-link-traversal](https://github.com/RubenEschauzier/comunica-feature-link-traversal/tree/feature/track-topology).
Follow the instructions in both README files.

Given you installed `comunica` in `path/to/comunica` and `comunica-feature-link-traversal` in `path/to/comunica-feature-link-traversal`, set the `workspaces` entry of `package.json` of `comunica-feature-link-traversal` to:

```json
  "workspaces": [
    "engines/*",
    "packages/*",
    "/path/to/comunica/packages/*",
    "/path/to/comunica/engines/*"
  ],
```
After, do 

```bash
cd path/to/comunica-feature-link-traversal
yarn install
```

## Tracking the Topology

To track the topology queried during LTQP move to the root of the `comunica-feature-link-traversal` repository and run

```bash
node engines/query-sparql-link-traversal-solid/bin/query.js -q "<query string>" --idp void --lenient --statisticsSaveLocation "/path/to/log-file.json"
```

This will save the required data to `log-file.json` during query execution.

## Creating an Interactive Visualization

In this repository, move your `log-file.json` to `temp-data/`. Then in `main.py` change `location` to point to your `log-file.json`. Then simply run `main.py` and your html output should appear in the browser.
