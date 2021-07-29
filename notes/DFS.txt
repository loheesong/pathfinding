DFS(Maze maze, Node start, Node end)
{
  // Put the start node in the stack
  start.visite = true;
  Stack stack(start);
  // While there is node to be handled in the queue
  while (!stack.empty())
  {
    // Handle the node in the front of the line
    Node curNode = queue.pop();
    // Terminate if the goal is reached
    if (curNode == end)
      break;
    // Take unvisited neighbors in order 
    // set its parent, mark as visited, and add to the queue
    auto neighbors = curNode.GetUnvisitedNeighbors();
    for (auto i = 0; i < neighbors.size(); ++i)
    {
      neighbors[i].visite = true;
      neighbors[i].parent = curNode;
      stack.push(neighbors[i]);
    }
  }
  // Done ! At this point we just have to walk back from the end using the parent
  // If end does not have a parent, it means that it has not been found.
}