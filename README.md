# Milestone 4: Google Pub/Sub communication for Microservices
## Objective:
* Get familiar with microservices.
* Implement microservice using Python.
* Containerize Python application.
* Configure Pub/Sub Subscription(s) to filter the receiving messages.

## Repository:
[https://github.com/GeorgeDaoud3/SOFE4630U-MS4](https://github.com/GeorgeDaoud3/SOFE4630U-MS4)

## Introduction 
1. See the following video for [the foundations of microservices](https://www.youtube.com/watch?v=lL_j7ilk7rc).
2. Read this document about [Event-driven architecture with Pub/Sub](https://cloud.google.com/solutions/event-driven-architecture-pubsub). Focus on the **event filter** technique, its advantages, limitations, and implementation. The microservices implemented in the milestone will use this technique to communicate.3. The milestone would implement a cloud solution for a cloud-based election system. It consists of
  1. **A voting machine**
     * A Python script that will run on a local machine to simulate a real voting machine.]
     * First, it asks for the **election ID** and the **machine ID**.
     * Then, it generates random votes and sends them to a **voting logger** service.
     * Finally, it will wait 
     * There will be three expected outputs: 
        1. **Already voted** if a vote with the same **voter ID** was processed before.
        2. **A vote was recorded successfully**.
        3. **Time out** if the vote processing takes much longer than expected.
     * You can run multiple script instances but with different **machine ID**. 
  2. A **voting logger** service.
     * The service accesses a Redis server to store the IDs of the voters who have already been voted on.
     * When a vote is received,
        * Redis will be checked for the **voter ID**.
        * If the **voter ID** exists, an **Already voted** message will be sent to the voting machine.
        * Otherwise,
           * The **voter ID** will be stored in the Redis database to prevent the voter from repeating the vote.
           * After excluding the **voter ID** (for voter privacy policy), the voting information will be sent to the **voting record** service.
  3. A **voting record** service.
     * The service uses a **PostgreSQL** server to store the votes.
     * Once, a **voting record** is received, it will be stored in a the **PostgreSQL** server.
     * Then a **A vote was recorded successfully** will be sent to the **voting machine**.
     

     
