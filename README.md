# spotify2youtube-playlist-synchronizer
API for synchronysing spotify playlist to youtube & to other devices for offline listening. The provides one-stop solution for song lovers and provides instructions on how to sync songs across spotify, youtube and the offline collection for handheld devices (namely smart phones).

## Pipeline stages
A pipeline for synchronysing a spotify playlist to youtube. It consists of multiple stages of message passing that ensure the added song syncs across multiple stages. Each of these stages are asynchronous and do not require any manual intrupt.

### Stage 1: Spotify Save to Spotify Playlist (via IFTTT)  
Whenever a user saves a song in the Spotify Save section, it gets added in the specified playlist. An IFTTT applet does this job perfectly. 

### Stage 2: Spotify Playlist to API server (via IFTTT)  
When the song gets added to the playlist via the IFTTT applet, another applet triggers that makes a web request that send the song information to out API server.

### Stage 3: API server to Youtube Playlist (uses Youtube API)  
Once the API server receives the song details, it heuristically selects the best song from the results obtained using the Youtube API search. The heuristic is basic and prefers songs uploaded by official verified users over other songs. The selected song then gets added to the youtube playlist.

### Stage 4: API server to Offline (using youtube-dl)  
Once the youtube playlist is synced, the playlist can be downloaded offline using the provided script. It also makes sure the tracks are in the same order as in the youtube playlist using appropriate track_number. This provides extra benefit if your mobile audio player supports sorting by track_number.


### Stage 5: Offline to Cloud  
If you need to sync the offline songs to cloud for syncing across devices, then here are the following options:
  - **Dropbox**: Setup the folder for offline sync in the Dropbox directory. This will sync your songs to cloud. Dropbox provides sufficient storage for a decent song collection.

### Stage 5: Cloud to Android  
- FolderSync: For android devices you can setup Folder sync to periodically sync your song collection on you handheld devices. You can specify the interval as per your need(Generally, I sync my collection on weekends).

All the above steps once combined will provide seamless song syncing across services & devices.
