# GenreX API Documentation

A Generative Music AI for Your Application.
Welcome to GenreX API for generative AI music!

At GenreX, we are passionate about blending technology with creativity to transform music. This API service is crafted for developers who seek to integrate state-of-the-art generative AI music into their applications, enhancing user experiences with unique and high-quality soundscapes.

Designed for a broad range of applications—from gaming to video creation—GenreX API uses advanced AI algorithms to compose and generate adaptive music in real-time. Whether you are looking to enrich your app’s audio environment or create personalized sound experiences, GenreX API is here to help you achieve your vision.

## PREREQUISITE
To access GenreX API, you must obtain the keys from the platform.
To generate music via API, follow these two steps:
1. Request the generation and immediately receive the `queryID` via the endpoint `v1/text2music/generateMusic`.
2. Obtain the audio URL by continuously checking the query status using the `queryID` in a loop until it is completed via the endpoint `v1/text2music/retrieve`.

Both steps require a user signature to verify identity.

---

## Authentication / Headers

**gx-key** (string, Required): your-api-key
**gx-signature** (string, Required): To generate the gx-signature, follow these steps:
1. Convert the payload object to a JSON string.
2. Concatenate the current timestamp and the JSON string with a dot (.) to form the string to be signed e.g. `${timestamp}.${payload}`
3. Use the `sha256-HMAC` algorithm and `your-api-secret` to sign the string, generating a hexadecimal string signature.
4. The gx-signature field value should be formatted as `t=timestamp,v=signature`.

**Content-Type** (string, Required): Must be set to `application/json`.

---

## Endpoints

### 1. Request Generation
Submit a generation request to the backend.

**POST** `https://api.genrex.com/v1/text2music/generateMusic`

**Request Body:**
- `duration` (integer, Required): The duration of music. The value must be between 5 seconds and 60 seconds.
- `text` (string, Required): The prompt text of the generation. The string must be between 1 and 250 characters.

**Response:**
- `id` (string): The id is used to check if the generation query is complete.
- `processSystem` (string): The versioning of AI
- `source` (string): The source of the request
- `status` (string): The status of the generation (Processing, Failed, or Completed).
- `content` (object)
- `metadata` (array or null)
- `userId` (string)
- `createdAt` (string)
- `updatedAt` (string)

---

### 2. Audio Retrieval
Retrieve audio assets and generation status by queryid.

**POST** `https://api.genrex.com/v1/text2music/retrieve`

**Request Body:**
- `queryId` (string, Required): This queryId is obtained from the initial generation request and is used to track the status and retrieve the generated audio content.

**Response:**
Returns the same response structure as Generation, but when `status` is `Completed`, the `response` array will contain the audio assets:
- `response` (array): The main array for audio assets retrieval.
  - `id` (string): The responseId
  - `metadata` (array): Includes `volume_visualize` array (normalized volume by timestep, scale 0-127, 1000 discrete segments).
  - `contentType` (string)
  - `content` (array): Contains objects with `url` (string) which is the URL of the generated audio file.
  - `queryId` (string)
  - `createdAt` (string)
  - `updatedAt` (string)

---

### 3. Get Balance
Retrieve the account generation credit balance.

**POST** `https://api.genrex.com/v1/text2music/getBalance`

**Request Body:**
The submitted `${payload}` must be assigned as a string in the form of `{}`.

**Response:**
- `maxDurationSeconds` (integer): The maximum duration (in seconds) allowed for each API session.
- `totalCreditQuota` (integer): The total amount of credits allocated to the user.
- `creditsUsed` (integer): The amount of credits that have already been used by the user.
- `userId` (string)
- `createdAt` (string)
- `updatedAt` (string)
