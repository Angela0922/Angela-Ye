const CHILD_NAME_KEY = "appleParkChildName";

const characters = [
  {
    id: "wren",
    displayName: "Wren",
    traits: ["tea parties", "story time", "blue muslin dress", "rosy cheeks", "red pigtails"],
    color: "#7ba7c9",
  },
  {
    id: "paloma",
    displayName: "Paloma in Teal Muslin",
    traits: ["sharing", "taking turns", "kindness", "teal muslin romper", "thoughtful heart"],
    color: "#5f9e9a",
  },
  {
    id: "luke",
    displayName: "Luke",
    traits: ["swings", "merry-go-rounds", "gentle encouragement", "yellow hair", "sunny patience"],
    color: "#6f8fbf",
  },
  {
    id: "gwen",
    displayName: "Gwen",
    traits: ["singing", "humming new songs", "joyful melodies", "black pigtails", "music"],
    color: "#b07d93",
  },
  {
    id: "levi",
    displayName: "Levi in Sage",
    traits: ["quiet walks", "watching clouds", "sage green outfit", "calm curiosity", "soft footsteps"],
    color: "#7d9a7b",
  },
  {
    id: "alex",
    displayName: "Alex",
    traits: ["building forts", "big ideas", "helpful hands", "laughing loudly", "adventure plans"],
    color: "#8a8f6d",
  },
  {
    id: "grady",
    displayName: "Grady",
    traits: ["collecting leaves", "asking questions", "warm smiles", "gentle bravery", "wonder"],
    color: "#9a7d62",
  },
  {
    id: "ella",
    displayName: "Ella in Pink Floral Dress",
    traits: ["pink floral dress", "flower crowns", "picnics", "sweet greetings", "blooming kindness"],
    color: "#d88aa5",
  },
  {
    id: "mia",
    displayName: "Mia in Dusty Rose",
    traits: ["dusty rose dress", "cozy cuddles", "bedtime stories", "soft blankets", "quiet comfort"],
    color: "#c58f96",
  },
];

function getChildName() {
  return localStorage.getItem(CHILD_NAME_KEY)?.trim() || "";
}

function saveChildName(name) {
  const trimmed = name.trim();
  if (trimmed) {
    localStorage.setItem(CHILD_NAME_KEY, trimmed);
  } else {
    localStorage.removeItem(CHILD_NAME_KEY);
  }
}

function pickRandom(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function getStoryPool(character, childName) {
  const name = character.displayName;
  const trait = pickRandom(character.traits);

  const sharedOpenings = [
    `On a breezy morning at Apple Park, ${name} woke up with a happy flutter in their heart.`,
    `The sun painted golden stripes across Apple Park while ${name} tied their shoes for a new day.`,
    `A little bird chirped above the apple trees as ${name} stepped onto the soft green grass.`,
    `Apple Park smelled like fresh leaves and warm sunshine, and ${name} was ready for something wonderful.`,
  ];

  const pools = {
    wren: [
      {
        title: "Wren's Tea Party in the Meadow",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Wren spread a tiny blanket beneath the apple trees and arranged cups for an imaginary tea party. With her ${trait} close at hand, she poured pretend chamomile for every friend she could dream up.`,
          `A ladybug landed on the rim of a cup, and Wren whispered, "You're invited too." She told a story about a brave acorn who rolled all the way to the pond, giggling when the acorn "splashed" in her imagination.`,
          `When the breeze carried the scent of apples, Wren packed up her tea set and skipped home, already planning tomorrow's party.`,
        ],
      },
      {
        title: "Story Time with Wren",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Wren curled beneath her favorite tree with a book she had made from folded paper. Her ${trait} fluttered as she read aloud to the quiet park, giving every squirrel a starring role.`,
          `She invented a tale about a rosy-cheeked explorer who found a door hidden inside an apple blossom. Each page turned with a soft rustle, like the park itself was listening.`,
          `As the sky turned pink, Wren closed her book and promised the trees she would return with a brand-new adventure tomorrow.`,
        ],
      },
    ],
    paloma: [
      {
        title: "Paloma Shares the Shiniest Swing",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Two children reached the swing at the very same moment. Paloma smiled in her ${trait} and said, "Let's take turns—ten pushes each."`,
          `She counted slowly and fairly, cheering for every soaring arc. When it was her turn, she went gently so the littlest friend wouldn't feel left behind.`,
          `By sunset, everyone had laughed, shared juice boxes, and agreed that Paloma's superpower was making fairness feel like fun.`,
        ],
      },
      {
        title: "The Kindness Blanket",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Paloma noticed a stuffed bunny sitting alone on a bench. She wrapped it in a small blanket from her bag, humming softly while she smoothed its ears.`,
          `Her ${trait} reminded her that caring for small things matters. She left the bunny where its owner would find it, with a note that said, "You are loved."`,
          `Walking home, Paloma felt warm inside, like the park had tucked a thank-you into the evening air.`,
        ],
      },
    ],
    luke: [
      {
        title: "Luke and the Tall Swing",
        paragraphs: [
          pickRandom(sharedOpenings),
          `A new friend stood nervously beside the tallest swing. Luke, with his ${trait}, gave the seat a gentle push and said, "I've got you."`,
          `Higher and higher they went, not too fast, not too wild—just enough to feel the wind and trust the rhythm.`,
          `When their feet touched earth again, the friend whispered, "Again?" Luke laughed and answered, "Always."`,
        ],
      },
      {
        title: "One More Spin",
        paragraphs: [
          pickRandom(sharedOpenings),
          `The merry-go-round gleamed in the afternoon light. Luke helped smaller kids climb on, steadying every step with ${trait}.`,
          `He ran alongside until the wheel spun on its own, then hopped on last so no one rode alone.`,
          `Round and round they went, dizzy with joy, while parents smiled from the shade of the apple trees.`,
        ],
      },
    ],
    gwen: [
      {
        title: "Gwen's Song for the Rain",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Raindrops began to tap the leaves, and Gwen started to hum. Her ${trait} turned the shower into a concert for worms, snails, and puddle-jumping boots.`,
          `She made up a chorus about silver skies and umbrella flowers, clapping on the second beat so friends could join in.`,
          `When the clouds parted, a rainbow arched over Apple Park, and Gwen bowed like a star finishing her best show.`,
        ],
      },
      {
        title: "The Melody in the Path",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Gwen walked the winding path, turning every pebble and breeze into notes. Her ${trait} helped her hear music where others heard only wind.`,
          `She taught a little tune to a child on a bench: hum, pause, hum again. Soon two voices became four, then a whole picnic table of singers.`,
          `The song had no name, but everyone agreed it sounded like friendship.`,
        ],
      },
    ],
    levi: [
      {
        title: "Levi Watches the Cloud Parade",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Levi lay on the grass in his ${trait}, studying clouds that drifted like slow ships. One looked like a rabbit; another like a spoon.`,
          `He did not rush. He simply watched and wondered how far a cloud travels before it becomes rain on another child's garden.`,
          `A butterfly landed on his knee, stayed for three breaths, and flew on. Levi smiled as if they had shared a secret.`,
        ],
      },
      {
        title: "The Quiet Trail",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Levi followed a mossy trail at the edge of Apple Park, listening to crunching leaves and distant laughter. His ${trait} made every step feel peaceful.`,
          `He found a feather, gray as morning fog, and placed it on a stump for the next wanderer to discover.`,
          `At home, Levi drew the feather in a notebook and wrote, "Some treasures are light enough to carry in your pocket."`,
        ],
      },
    ],
    alex: [
      {
        title: "Alex Builds a Leaf Fort",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Alex gathered sticks and armfuls of leaves, stacking them into the coziest fort Apple Park had ever seen. ${trait} kept the walls steady while imagination filled the roof.`,
          `"Knock knock," called a friend. "Room for one more?" Alex swept aside leaves to make a doorway wide enough for everyone.`,
          `Inside, they told jokes, shared crackers, and named their fort The Whispering Apple because the trees seemed to lean in and listen.`,
        ],
      },
      {
        title: "The Big Idea",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Alex stood on a stump like a captain and announced a plan: a treasure hunt from the pond to the playground. ${trait} made the whole crew cheer.`,
          `Clues were simple—three red leaves, a feather by the bench, a smooth stone near the slide. Each discovery felt like winning a medal.`,
          `The real treasure was a basket of apples waiting at the finish. Alex declared, "Adventure tastes best when shared."`,
        ],
      },
    ],
    grady: [
      {
        title: "Grady's Leaf Collection",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Grady knelt beside a maple tree, choosing leaves shaped like stars and hearts. His ${trait} helped him notice colors other people walked past.`,
          `He pressed each leaf between the pages of a book and labeled them with careful letters: gold, rust, brave green.`,
          `At supper he showed his family the collection, and his little sister asked to start one of her own tomorrow.`,
        ],
      },
      {
        title: "One Brave Question",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Grady wondered why fireflies glow at dusk, so he asked the park ranger, the baker, and even the crossing guard. ${trait} led him to patient answers.`,
          `Some grown-ups said, "Great question." One said, "Let's look it up together." Grady wrote the answer in big looping letters.`,
          `That night he watched the first firefly blink near his window and whispered, "Hello, little lantern."`,
        ],
      },
    ],
    ella: [
      {
        title: "Ella's Flower Crown Picnic",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Ella twirled in her ${trait}, weaving daisies into crowns for anyone who passed by. Each crown came with a compliment: "Your smile is sunshine."`,
          `She spread a picnic blanket with sandwiches cut into stars and strawberries that stained fingers pink.`,
          `Friends sat in a circle, crowns slightly crooked, laughing until the crumbs looked like confetti on the grass.`,
        ],
      },
      {
        title: "The Blossom Bridge",
        paragraphs: [
          pickRandom(sharedOpenings),
          `After a spring shower, Ella found petals scattered across the path like a pink bridge. Her ${trait} seemed to glow in the soft light.`,
          `She gathered the brightest petals and laid them along the bench so the next walker would feel welcomed.`,
          `A toddler pointed and clapped. Ella curtsied and said, "The flowers wanted to say hello."`,
        ],
      },
    ],
    mia: [
      {
        title: "Mia's Cozy Blanket Hour",
        paragraphs: [
          pickRandom(sharedOpenings),
          `Mia spread a soft blanket under the old apple tree, wearing her ${trait} like a hug. She opened a picture book and patted the space beside her.`,
          `One by one, tired little friends sat down. Mia read slowly, letting every page breathe, until yawns floated like tiny clouds.`,
          `The park grew quiet and kind. Even the squirrels seemed to tiptoe past the story's gentle ending.`,
        ],
      },
      {
        title: "Dusty Rose at Dusk",
        paragraphs: [
          pickRandom(sharedOpenings),
          `As the sky turned lavender, Mia walked the loop with a lantern jar that held no fire—only captured twilight. ${trait} made her steps feel like a lullaby.`,
          `She waved to parents pushing strollers and to teenagers still laughing on the swings, wishing each of them a soft night.`,
          `At her window, Mia placed the jar on a shelf and fell asleep dreaming of apple-scented stars.`,
        ],
      },
    ],
    child: [
      {
        title: `${childName}'s Apple Park Discovery`,
        paragraphs: [
          `On a sparkling morning at Apple Park, ${childName} ran through the gate with shoes that somehow already felt muddy.`,
          `${childName} followed a trail of golden leaves to a bench no one else seemed to notice. Sitting down, ${childName} heard the trees whispering secrets about hidden acorns and friendly ladybugs.`,
          `A breeze carried the smell of apples and adventure. ${childName} decided to build a tiny museum of treasures: one feather, two smooth stones, and a leaf shaped exactly like a heart.`,
          `When the sun began to set, ${childName} waved goodbye to Apple Park, knowing tomorrow would hold a brand-new story.`,
        ],
      },
      {
        title: `The Day ${childName} Made the Park Laugh`,
        paragraphs: [
          `${childName} arrived at Apple Park with pockets full of questions and a smile that could brighten cloudy days.`,
          `Near the playground, ${childName} invented a game called "Kindness Tag"—if you tagged someone, you had to say one nice thing before running again.`,
          `Soon children, parents, and even a dog with floppy ears were playing. Laughter rolled across the grass like a happy thunder.`,
          `As stars appeared, ${childName} walked home feeling proud. Apple Park felt proud too, in the quiet way places do when they have been loved well.`,
        ],
      },
      {
        title: `${childName} and the Whispering Apple Tree`,
        paragraphs: [
          `Apple Park was extra green the day ${childName} found the oldest tree in the meadow. Its bark was rough like a storybook cover.`,
          `${childName} pressed a palm against the trunk and listened. The tree did not use words, but ${childName} understood anyway: slow down, look closely, be brave and gentle at once.`,
          `A red apple had fallen nearby. ${childName} placed it at the roots as a thank-you gift and drew the tree in a notebook with roots deep as kindness.`,
          `That night ${childName} dreamed of branches that reached all the way to the moon, just to tuck in every child in town.`,
        ],
      },
    ],
  };

  return pools[character.id];
}

function buildRoster(childName) {
  const roster = [...characters];
  if (childName) {
    roster.push({
      id: "child",
      displayName: childName,
      traits: ["curiosity", "kindness", "bravery", "wonder", "joy"],
      color: "#d4a05a",
    });
  }
  return roster;
}

function renderStory() {
  const childName = getChildName();
  const roster = buildRoster(childName);
  const character = pickRandom(roster);
  const stories = getStoryPool(character, childName);

  if (!stories?.length) {
    return;
  }

  const story = pickRandom(stories);
  const badge = document.getElementById("character-badge");
  const title = document.getElementById("story-title");
  const body = document.getElementById("story-body");
  const card = document.getElementById("story-card");

  badge.textContent = `Featuring ${character.displayName}`;
  badge.style.background = `${character.color}33`;
  badge.style.color = character.color;

  title.textContent = story.title;
  body.innerHTML = story.paragraphs.map((paragraph) => `<p>${paragraph}</p>`).join("");

  card.style.animation = "none";
  void card.offsetWidth;
  card.style.animation = "fadeUp 0.7s ease";
}

function initSettings() {
  const input = document.getElementById("child-name");
  const saveButton = document.getElementById("save-name");
  const savedName = getChildName();

  if (savedName) {
    input.value = savedName;
  }

  saveButton.addEventListener("click", () => {
    saveChildName(input.value);
    renderStory();
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      saveChildName(input.value);
      renderStory();
    }
  });
}

document.getElementById("refresh-btn").addEventListener("click", () => {
  renderStory();
});

initSettings();
renderStory();
