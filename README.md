# ICLR-Barycenter

Let's have our next conference at the barycenter of ML research!

We parse the proceedings of ICLR 2023 to obtain the location of each paper's authors.
We then scrape the web for visa restrictions and airfare between these locations and use the resulting graph to minimize the total earth mover's distance of transporting thousands of ML scientists to the proposed optimal conference location.

We then extend our code to support other constraints, such as going to NeurIPS instead of ICLR, or transporting only the last author of each accepted paper.

Solving an optimal transport problem for reviewer number 2 is left as an exercise to the reader.
