const express = require("express")
const admin = require("firebase-admin")
const cors = require("cors")

const serviceAccount = require("./admin-key.json")

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
})

const db = admin.firestore()
const app = express()
const port = 3000

app.use(cors())
app.use(express.json())

app.get("/", (req, res) => {
  res.send("CureZ DB server is running!")
})

app.post("/signup", async (req, res) => {
  const { uid, email, name, age, gender, emailVerified } = req.body

  if (!uid || !email) {
    return res.status(400).send({ error: "Missing uid or email." })
  }

  try {
    let userRecord
    try {
      userRecord = await admin.auth().getUser(uid)
    } catch (error) {
      userRecord = await admin.auth().getUserByEmail(email)
    }

    const profileData = {
      email,
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    }

    if (typeof emailVerified === "boolean") {
      profileData.emailVerified = emailVerified
    }

    if (name) {
      profileData.name = name
    }

    if (gender) {
      profileData.gender = gender
    }

    if (age !== undefined && age !== null && age !== "") {
      const numericAge = Number.parseInt(age, 10)
      if (!Number.isNaN(numericAge)) {
        profileData.age = numericAge
      }
    }

    await db.collection("users").doc(userRecord.uid).set(profileData, { merge: true })

    if (name && userRecord.displayName !== name) {
      try {
        await admin.auth().updateUser(userRecord.uid, { displayName: name })
      } catch (error) {
        console.warn("Failed to update display name:", error.message)
      }
    }

    res.status(200).send({ uid: userRecord.uid })
  } catch (error) {
    res.status(500).send({ error: error.message })
  }
})

app.post("/login", async (req, res) => {
  const { email } = req.body

  if (!email) {
    return res.status(400).send({ error: "Email is required." })
  }

  try {
    const userRecord = await admin.auth().getUserByEmail(email)

    if (!userRecord.emailVerified) {
      return res.status(403).send({ error: "Please verify your email before logging in." })
    }

    const userDoc = await db.collection("users").doc(userRecord.uid).get()
    const profile = userDoc.exists ? userDoc.data() : null

    res.status(200).send({ uid: userRecord.uid, profile })
  } catch (error) {
    res.status(401).send({ error: "Unable to locate account for the provided email." })
  }
})

app.post("/save-summary", async (req, res) => {
  const { uid, summary } = req.body
  if (!uid || !summary) {
    return res.status(400).send({ error: "Missing uid or summary" })
  }

  try {
    const userRef = db.collection("users").doc(uid)
    await userRef.set({ latestSummary: summary }, { merge: true })
    res.status(200).send({ message: "Summary saved successfully" })
  } catch (error) {
    res.status(500).send({ error: error.message })
  }
})

app.post("/save-name", async (req, res) => {
  const { uid, name } = req.body
  if (!uid || !name) {
    return res.status(400).send({ error: "Missing uid or name" })
  }

  try {
    const userRef = db.collection("users").doc(uid)
    await userRef.set({ name }, { merge: true })
    res.status(200).send({ message: "Name saved successfully" })
  } catch (error) {
    res.status(500).send({ error: error.message })
  }
})

app.post("/update-profile", async (req, res) => {
  const { uid, name, age, gender, emailVerified } = req.body
  if (!uid) {
    return res.status(400).send({ error: "Missing uid" })
  }

  try {
    const userRef = db.collection("users").doc(uid)
    const updateData = {}

    if (name !== undefined) updateData.name = name
    if (age !== undefined && age !== "") updateData.age = Number.parseInt(age, 10)
    if (gender !== undefined) updateData.gender = gender
    if (typeof emailVerified === "boolean") updateData.emailVerified = emailVerified

    await userRef.set(updateData, { merge: true })
    res.status(200).send({ message: "Profile updated successfully" })
  } catch (error) {
    res.status(500).send({ error: error.message })
  }
})

app.get("/get-summary/:uid", async (req, res) => {
  const { uid } = req.params
  try {
    const userRef = db.collection("users").doc(uid)
    const doc = await userRef.get()
    if (!doc.exists) {
      res.status(404).send({ error: "No summary found for this user." })
    } else {
      res.status(200).send(doc.data())
    }
  } catch (error) {
    res.status(500).send({ error: error.message })
  }
})

app.get("/user/:uid", async (req, res) => {
  const { uid } = req.params
  try {
    const userRef = db.collection("users").doc(uid)
    const doc = await userRef.get()
    if (!doc.exists) {
      res.status(404).send({ error: "User not found" })
    } else {
      const userData = doc.data()
      res.status(200).send({ uid, ...userData })
    }
  } catch (error) {
    res.status(500).send({ error: error.message })
  }
})

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`)
})