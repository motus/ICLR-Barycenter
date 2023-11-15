# ICLR-Barycenter

Let's have our next conference at the barycenter of ML research!

We build a graph of ML researchers' locations and distances between them.
To obtain the vertices, we parse the proceedings of ICLR 2023 and extract the locations of each paper's authors.
Then we scrape the web for visa requirements and airfare between these locations and use that data to label the arcs of the graph.
Finally, we minimize the total earth mover's distance of transporting thousands of ML scientists and propose an optimal location of the next conference.

Solving an optimal transport problem of sending all reviewers number 2 to a single destination is left as an exercise to the reader.
