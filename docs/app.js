const state = {
  games: [],
  gamesStatus: "loading",
  selectedCompetitions: new Set(),
};

const form = document.querySelector("#search-form");
const submitButton = form.querySelector('[type="submit"]');
const pageShell = document.querySelector(".page-shell");
const pageHeader = document.querySelector(".page-header");
const searchPanel = document.querySelector(".search-panel");
const updateBadge = document.querySelector("#update-badge");
const updateTime = document.querySelector("#update-time");
const dateInput = document.querySelector("#date-input");
const timeInput = document.querySelector("#time-input");
const timeField = document.querySelector("#time-field");
const competitionPicker = document.querySelector("#competition-picker");
const competitionTrigger = document.querySelector("#competition-input");
const competitionSummary = document.querySelector("#competition-summary");
const competitionOptions = document.querySelector("#competition-options");
const competitionOptionsList = competitionOptions.querySelector(
  ".competition-options-inner",
);
const wholeDayInput = document.querySelector("#whole-day-input");
const resetButton = document.querySelector("#reset-button");
const results = document.querySelector("#results");
const resultsSection = document.querySelector(".results-section");
const statusMessage = document.querySelector("#status-message");
const resultCount = document.querySelector("#result-count");
const reducedMotionQuery = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
);
let competitionHideTimer;
let resultsSequence = 0;

function setStatus(message) {
  statusMessage.hidden = false;
  statusMessage.textContent = message;
  results.replaceChildren();
  resultCount.textContent = "";
}

function setDefaultDate() {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  dateInput.value = `${year}-${month}-${day}`;
}

function setGamesStatus(status) {
  state.gamesStatus = status;
  form.setAttribute("aria-busy", String(status === "loading"));
  submitButton.disabled = status === "loading";
  competitionTrigger.disabled = status !== "ready";
}

function updateCompetitionSummary() {
  const selectedNames = [...state.selectedCompetitions].sort();

  if (selectedNames.length === 0) {
    competitionSummary.textContent = "All competitions";
    competitionTrigger.removeAttribute("title");
  } else if (selectedNames.length === 1) {
    competitionSummary.textContent = selectedNames[0];
    competitionTrigger.title = selectedNames[0];
  } else {
    competitionSummary.textContent = `${selectedNames.length} competitions selected`;
    competitionTrigger.title = selectedNames.join(", ");
  }
}

function setCompetitionPicker(isOpen) {
  const wasOpen = competitionTrigger.getAttribute("aria-expanded") === "true";

  if (isOpen === wasOpen) {
    return;
  }

  competitionTrigger.setAttribute("aria-expanded", String(isOpen));
  competitionOptions.inert = !isOpen;

  if (isOpen) {
    window.clearTimeout(competitionHideTimer);
    competitionOptions.hidden = false;
    competitionOptions.removeAttribute("aria-hidden");

    // Commit the collapsed state before expanding so the first opening animates.
    void competitionOptions.offsetHeight;
    competitionPicker.classList.add("is-open");
    return;
  }

  competitionPicker.classList.remove("is-open");
  competitionOptions.setAttribute("aria-hidden", "true");

  if (reducedMotionQuery.matches) {
    competitionOptions.hidden = true;
    return;
  }

  competitionHideTimer = window.setTimeout(() => {
    if (competitionTrigger.getAttribute("aria-expanded") === "false") {
      competitionOptions.hidden = true;
    }
  }, 300);
}

competitionOptions.addEventListener("transitionend", (event) => {
  if (
    event.target === competitionOptions &&
    event.propertyName === "grid-template-rows" &&
    competitionTrigger.getAttribute("aria-expanded") === "false"
  ) {
    window.clearTimeout(competitionHideTimer);
    competitionOptions.hidden = true;
  }
});

function populateCompetitions(games) {
  const names = [...new Set(games.map((game) => game.competitionName))].sort();

  for (const name of names) {
    const option = document.createElement("label");
    option.className = "competition-option";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.name = "competitions";
    checkbox.value = name;

    const optionText = document.createElement("span");
    optionText.textContent = name;

    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        state.selectedCompetitions.add(name);
      } else {
        state.selectedCompetitions.delete(name);
      }

      updateCompetitionSummary();
    });

    option.append(checkbox, optionText);
    competitionOptionsList.append(option);
  }
}

function isValidGame(game) {
  const requiredStrings = [
    "id",
    "date",
    "homeTeam",
    "awayTeam",
    "competitionName",
    "detailsUrl",
  ];

  return (
    game !== null &&
    typeof game === "object" &&
    requiredStrings.every(
      (field) =>
        typeof game[field] === "string" && game[field].trim().length > 0,
    ) &&
    (game.time === null || typeof game.time === "string")
  );
}

function filterGames() {
  const selectedDate = dateInput.value;
  const selectedTime = timeInput.value;
  const showWholeDay = wholeDayInput.checked;

  if (!selectedDate) {
    return [];
  }

  return state.games.filter((game) => {
    if (game.date !== selectedDate) {
      return false;
    }

    if (
      state.selectedCompetitions.size > 0 &&
      !state.selectedCompetitions.has(game.competitionName)
    ) {
      return false;
    }

    if (!showWholeDay && selectedTime && game.time !== selectedTime) {
      return false;
    }

    return true;
  });
}

function createMatchCard(game) {
  const article = document.createElement("article");
  const titleId = `match-${game.id}`;
  article.className = "match-card";
  article.setAttribute("aria-labelledby", titleId);

  const kickoff = document.createElement("div");
  kickoff.className = "match-kickoff";

  const timeElement = document.createElement("span");
  timeElement.className = "match-time";
  timeElement.textContent = game.time ?? "Time TBA";

  if (game.time === null) {
    timeElement.classList.add("missing");
    kickoff.classList.add("missing");
    kickoff.setAttribute("aria-label", "Kickoff time to be confirmed");
  } else {
    kickoff.setAttribute("aria-label", `Kickoff at ${game.time}`);
  }

  kickoff.append(timeElement);

  const content = document.createElement("div");
  content.className = "match-content";

  const teams = document.createElement("h3");
  teams.className = "match-teams";
  teams.id = titleId;

  const homeTeam = document.createElement("span");
  homeTeam.className = "team";
  homeTeam.textContent = game.homeTeam;

  const versus = document.createElement("span");
  versus.className = "versus";
  versus.textContent = "vs";

  const awayTeam = document.createElement("span");
  awayTeam.className = "team";
  awayTeam.textContent = game.awayTeam;

  teams.append(homeTeam, versus, awayTeam);

  const meta = document.createElement("div");
  meta.className = "match-meta";

  const labels = [game.competitionName, game.sectionName].filter(Boolean);

  for (const label of labels) {
    const pill = document.createElement("span");
    pill.textContent = label;
    pill.title = label;
    meta.append(pill);
  }

  const link = document.createElement("a");
  link.className = "match-link";
  link.href = game.detailsUrl;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = "↗";
  link.setAttribute(
    "aria-label",
    `${game.homeTeam} versus ${game.awayTeam} in Matchcenter (opens in a new tab)`,
  );

  content.append(teams, meta);
  article.append(kickoff, content, link);

  return article;
}

function renderGames(games) {
  results.replaceChildren();

  if (games.length === 0) {
    setStatus("No matching fixtures found.");
    return;
  }

  statusMessage.hidden = true;
  resultCount.textContent = `${games.length} ${
    games.length === 1 ? "match" : "matches"
  }`;

  for (const game of games) {
    results.append(createMatchCard(game));
  }
}

function scrollToResults(sequence) {
  requestAnimationFrame(() => {
    if (sequence !== resultsSequence) {
      return;
    }

    const viewportMargin = 24;
    const panelHeight = resultsSection.offsetHeight;
    const canCenter = panelHeight <= window.innerHeight - viewportMargin * 2;
    const viewportOffset = canCenter
      ? (window.innerHeight - panelHeight) / 2
      : viewportMargin;
    const bottomSpace = Math.max(viewportOffset + 32, 64);

    pageShell.style.setProperty("--page-bottom-space", `${bottomSpace}px`);

    let documentTop = 0;
    let element = resultsSection;

    while (element) {
      documentTop += element.offsetTop;
      element = element.offsetParent;
    }

    const targetTop = documentTop - viewportOffset;

    resultsSection.focus({ preventScroll: true });
    window.scrollTo({
      behavior: reducedMotionQuery.matches ? "auto" : "smooth",
      top: Math.max(targetTop, 0),
    });
  });
}

let heroScrollFrame = null;

function updateHeroFromScroll() {
  const progress = Math.min(Math.max(window.scrollY / 360, 0), 1);
  pageHeader.style.setProperty("--title-scale", 1 - progress * 0.2);
  pageHeader.style.setProperty("--intro-scale", 1 - progress * 0.12);
  pageHeader.style.setProperty("--hero-shift", `${progress * 18}px`);
  pageHeader.style.setProperty("--intro-opacity", 1 - progress * 0.18);
  searchPanel.style.setProperty("--search-scale", 1 - progress * 0.1);
  searchPanel.style.setProperty("--search-shift", `${progress * 18}px`);
  searchPanel.style.setProperty("--search-opacity", 1 - progress * 0.18);
  resultsSection.style.setProperty("--results-scale", 0.9 + progress * 0.1);
  resultsSection.style.setProperty("--results-shift", `${(1 - progress) * 18}px`);
  resultsSection.style.setProperty(
    "--results-opacity",
    0.78 + progress * 0.22,
  );
  heroScrollFrame = null;
}

function scheduleHeroUpdate() {
  if (heroScrollFrame === null) {
    heroScrollFrame = requestAnimationFrame(updateHeroFromScroll);
  }
}

function resetFilterValues() {
  form.reset();
  state.selectedCompetitions.clear();
  updateCompetitionSummary();
  setCompetitionPicker(false);
  syncTimeInput();
  setDefaultDate();
}

function completeReset(sequence) {
  if (sequence !== resultsSequence) {
    return;
  }

  resultsSection.hidden = true;
  resultsSection.classList.remove("is-dismissing");
  setStatus("Choose filters and select “Find matches”.");
  pageShell.style.removeProperty("--page-bottom-space");
}

function dismissResults(sequence) {
  if (resultsSection.hidden) {
    completeReset(sequence);
    return;
  }

  resultsSection.inert = true;

  if (reducedMotionQuery.matches) {
    window.scrollTo({ top: 0, behavior: "auto" });
    completeReset(sequence);
    return;
  }

  if (window.scrollY <= 4) {
    // At the top there is no scroll-driven shrink, so play it explicitly.
    resultsSection.classList.add("is-dismissing");
    window.setTimeout(() => completeReset(sequence), 300);
    return;
  }

  const startedAt = performance.now();

  window.scrollTo({ top: 0, behavior: "smooth" });

  function finishAfterScroll() {
    if (sequence !== resultsSequence) {
      return;
    }

    if (window.scrollY <= 2 || performance.now() - startedAt >= 1600) {
      completeReset(sequence);
      return;
    }

    requestAnimationFrame(finishAfterScroll);
  }

  requestAnimationFrame(finishAfterScroll);
}

function syncTimeInput() {
  timeInput.disabled = wholeDayInput.checked;
  timeField.classList.toggle("is-disabled", wholeDayInput.checked);
}

async function loadMetadata() {
  try {
    const response = await fetch("./data/metadata.json", { cache: "no-cache" });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const metadata = await response.json();

    if (typeof metadata?.generatedAt !== "string") {
      throw new Error("Missing generatedAt timestamp");
    }

    const generatedAt = new Date(metadata.generatedAt);

    if (Number.isNaN(generatedAt.getTime())) {
      throw new Error("Invalid generatedAt timestamp");
    }

    const formattedTimestamp = new Intl.DateTimeFormat("de-CH", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hourCycle: "h23",
      timeZone: "Europe/Zurich",
    })
      .format(generatedAt)
      .replace(", ", " · ");

    updateTime.dateTime = metadata.generatedAt;
    updateTime.textContent = formattedTimestamp;
    updateBadge.hidden = false;
  } catch (error) {
    console.warn("Could not load update metadata.", error);
  }
}

async function loadGames() {
  setStatus("Loading fixtures…");

  try {
    const response = await fetch("./data/games.json", { cache: "no-cache" });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const games = await response.json();

    if (!Array.isArray(games) || !games.every(isValidGame)) {
      throw new Error("Invalid games data");
    }

    populateCompetitions(games);
    state.games = games;
    setGamesStatus("ready");
    setStatus("Choose filters and select “Find matches”.");
  } catch (error) {
    state.games = [];
    setGamesStatus("error");
    console.error(error);
    setStatus("Could not load fixture data.");
  }
}

wholeDayInput.addEventListener("change", syncTimeInput);

competitionTrigger.addEventListener("click", () => {
  const isOpen = competitionTrigger.getAttribute("aria-expanded") === "true";
  setCompetitionPicker(!isOpen);
});

competitionTrigger.addEventListener("keydown", (event) => {
  if (event.key === "ArrowDown") {
    event.preventDefault();
    setCompetitionPicker(true);
    competitionOptions.querySelector("input")?.focus();
  }
});

competitionPicker.addEventListener("focusout", () => {
  requestAnimationFrame(() => {
    if (!competitionPicker.contains(document.activeElement)) {
      setCompetitionPicker(false);
    }
  });
});

document.addEventListener("keydown", (event) => {
  if (
    event.key === "Escape" &&
    competitionTrigger.getAttribute("aria-expanded") === "true"
  ) {
    setCompetitionPicker(false);
    competitionTrigger.focus();
  }
});

document.addEventListener("click", (event) => {
  if (!competitionPicker.contains(event.target)) {
    setCompetitionPicker(false);
  }
});

if (!reducedMotionQuery.matches) {
  updateHeroFromScroll();
  window.addEventListener("scroll", scheduleHeroUpdate, { passive: true });
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const sequence = ++resultsSequence;

  setCompetitionPicker(false);
  resultsSection.classList.remove("is-dismissing");
  resultsSection.inert = false;
  resultsSection.hidden = false;

  if (state.gamesStatus === "ready") {
    renderGames(filterGames());
  } else {
    setStatus(
      state.gamesStatus === "loading"
        ? "Fixtures are still loading…"
        : "Could not load fixture data. Please refresh and try again.",
    );
  }

  scrollToResults(sequence);
});

resetButton.addEventListener("click", () => {
  const sequence = ++resultsSequence;

  resetButton.classList.remove("is-resetting");
  void resetButton.offsetWidth;
  resetButton.classList.add("is-resetting");
  resetFilterValues();
  dismissResults(sequence);
});

resetButton.addEventListener("animationend", () => {
  resetButton.classList.remove("is-resetting");
});

setDefaultDate();
loadMetadata();
loadGames();
