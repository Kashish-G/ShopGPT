const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");

let userText = null;

function handleResponsive() {
  var windowWidth = window.innerWidth;
  var cardContainer = document.querySelector('.card-container');

  if (windowWidth < 768) {
    cardContainer.classList.add('responsive');
  } else {
    cardContainer.classList.remove('responsive');
  }
}

//hiding delete and mode theme when textarea is clicked
const textarea = document.getElementById('chat-input');
const typingContainer = document.querySelector('.typing-container');

textarea.addEventListener('focus', () => {
  typingContainer.classList.add('hide-controls');
});

textarea.addEventListener('blur', () => {
  typingContainer.classList.remove('hide-controls');
});


// Event listener for window resize
window.addEventListener('resize', function () {
  handleResponsive();
});

handleResponsive();


const loadDataFromLocalstorage = () => {
  // Load saved chats and theme from local storage and apply/add on the page
  const themeColor = localStorage.getItem("themeColor");

  document.body.classList.toggle("light-mode", themeColor === "light_mode");
  themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";

  const defaultText = `<div class="default-text">
                            <h1>ShopGPT</h1>
                            <p>Start a conversation and explore the power of AI.<br> Your chat history will be displayed here.</p>
                        </div>`

  chatContainer.innerHTML = localStorage.getItem("all-chats") || defaultText;
  chatContainer.scrollTo(0, chatContainer.scrollHeight); // Scroll to bottom of the chat container
}

const createChatElement = (content, className) => {
  // Create new div and apply chat, specified class and set html content of div
  const chatDiv = document.createElement("div");
  chatDiv.classList.add("chat", className);
  chatDiv.innerHTML = content;
  return chatDiv; // Return the created chat div
}



const copyResponse = (copyBtn) => {
  // Copy the text content of the response to the clipboard
  const reponseTextElement = copyBtn.parentElement.querySelector("p");
  navigator.clipboard.writeText(reponseTextElement.textContent);
  copyBtn.textContent = "done";
  setTimeout(() => copyBtn.textContent = "content_copy", 1000);
}


const showTypingAnimation = () => {
  // Display the typing animation and call the handleOutgoingChat function
  const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="images/chatbot.jpg" alt="chatbot-img">
                        <div class="typing-animation">
                            <div class="typing-dot" style="--delay: 0.2s"></div>
                            <div class="typing-dot" style="--delay: 0.3s"></div>
                            <div class="typing-dot" style="--delay: 0.4s"></div>
                        </div>
                    </div>
                    <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
                </div>`;
  // Create an incoming chat div with typing animation and append it to chat container
  const incomingChatDiv = createChatElement(html, "incoming");
  chatContainer.appendChild(incomingChatDiv);
  chatContainer.scrollTo(0, chatContainer.scrollHeight);
  handleOutgoingChat();
};

// const showTypingAnimation = () => {
//   const html = `<div class="chat-content">
//                   <div class="chat-details">
//                       <img src="images/chatbot.jpg" alt="chatbot-img">
//                       <div class="typing-animation">
//                           <div class="typing-dot"></div>
//                           <div class="typing-dot"></div>
//                           <div class="typing-dot"></div>
//                       </div>
//                   </div>
//                   <span onclick="copyResponse(this)" class="material-symbols-rounded">content_copy</span>
//               </div>`;

//   const incomingChatDiv = createChatElement(html, "incoming");
//   chatContainer.appendChild(incomingChatDiv);
//   chatContainer.scrollTo(0, chatContainer.scrollHeight);
//   handleOutgoingChat();
// };

// showTypingAnimation();



const loadIntents = async () => {
  try {
    const response = await fetch("intents.json");
    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      console.error("Failed to fetch intents.json");
    }
  } catch (error) {
    console.error("Failed to load intents.json", error);
  }
};
const createProductCard = (product) => {
  return `<div class="product-card">
                <h3>${product.title}</h3>
                <p>Price: ${product.price}</p>
                <p>Available on ${product.platform}</p>
                <a href="${product.href}" target="_blank">See More</a>
            </div>`;
};

let intents = [];
loadIntents().then(data => {
  intents = data;
});

const handleOutgoingChat = async () => {
  userText = chatInput.value.trim();
  if (!userText) return;

  const displayText = userText.startsWith("I want ") ? userText.slice(7) : userText;
  userText = "I want " + userText;

  chatInput.value = "";
  chatInput.style.height = `${initialInputHeight}px`;

  const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="images/user.png" alt="user-img">
                        <p>${displayText}</p>
                    </div>
                </div>`;
  const outgoingChatDiv = createChatElement(html, "outgoing");
  chatContainer.querySelector(".default-text")?.remove();
  chatContainer.appendChild(outgoingChatDiv);
  chatContainer.scrollTo(0, chatContainer.scrollHeight);

  const matchedIntent = intents.find(intent =>
    intent.patterns.some(pattern => userText.toLowerCase().includes(pattern.toLowerCase()))
  );

  if (matchedIntent) {

    const html = `<div class="chat-content">
                        <div class="chat-details">
                            <img src="images/chatbot.png" alt="chatbot-img">
                            <p>%response%</p>
                        </div>
                    </div>`;
    if (matchedIntent.tag === "product_inquiry") {

      const responseIndex = Math.floor(Math.random() * matchedIntent.responses.length);
      const responseText = matchedIntent.responses[responseIndex];

      const html = `<div class="chat-content">
                <div class="chat-details">
                    <img src="images/chatbot.png" alt="chatbot-img">
                    <p>${responseText}</p>
                </div>
            </div>`;

      const responseDiv = createChatElement(html, "incoming");
      chatContainer.appendChild(responseDiv);


      try {
        const response = await fetch("http://localhost:3000/api/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
            "Access-Control-Allow-Headers": "Content-Type"
          },

          body: JSON.stringify({ query: userText }),
        });

        if (response.ok) {
          const data = await response.json();
          if (data.results.status === "success") {
            const products = data.results.data;
            if (products.length > 0) {
              const cardWrapper = document.createElement("div");
              cardWrapper.classList.add("card-wrapper");

              const platformContainers = {};
              let productCount = 0;
              let currentRow = null;

              for (const product of products) {
                const platform = product.platform;

                // Create a new platform container if it doesn't exist
                if (!platformContainers[platform]) {
                  const platformContainer = document.createElement("div");
                  platformContainer.classList.add("platform-container");

                  platformContainers[platform] = platformContainer;

                  // Create a new row for every 5 products
                  if (productCount % 5 === 0) {
                    currentRow = document.createElement("div");
                    currentRow.classList.add("card-row");
                    cardWrapper.appendChild(currentRow);
                  }
                }

                // Create and append the card elements to the current platform container
                const cardContainer = document.createElement("div");
                cardContainer.classList.add("card-container");


                const logoContainer = document.createElement("div");
                logoContainer.classList.add("logo-container");

                const platformLogo = document.createElement("img");
                platformLogo.src = `images/${product.platform}_logo.png`;
                platformLogo.classList.add("platform-logo");
                logoContainer.appendChild(platformLogo);
                cardContainer.appendChild(logoContainer);

                const cardImage = document.createElement("img");
                cardImage.src = product.img_url;
                cardImage.classList.add("card-image");
                cardContainer.appendChild(cardImage);



                const cardTitle = document.createElement("h2");
                cardTitle.textContent = product.title;
                cardContainer.appendChild(cardTitle);

                const cardRating = document.createElement("div");
                cardRating.classList.add("card-rating");

                const starIcon = document.createElement("img");
                
                starIcon.src = `images/star_icon.png`;
                starIcon.classList.add("star_icon");
                cardRating.appendChild(starIcon);

                if (product.rating && product.rating.trim() !== "" && product.rating !== "0") {
                  const ratingText = document.createElement("span");
                  ratingText.textContent = product.rating;
                  ratingText.classList.add("card-rating-text");
                  cardRating.appendChild(ratingText);
                }

                if (product.reviews && product.reviews.trim() !== "") {
                  const reviewsText = document.createElement("span");
                  reviewsText.textContent = `(${product.reviews})`;
                  reviewsText.classList.add("card-reviews-text");
                  cardRating.appendChild(reviewsText);
                }

                if (!product.rating || !product.reviews || (product.rating.trim() === "" && product.reviews.trim() === "")) {
                  const noRatingReviewsText = document.createElement("span");
                  noRatingReviewsText.textContent = "No Ratings and Reviews";
                  noRatingReviewsText.classList.add("card-rating-text");
                  cardRating.appendChild(noRatingReviewsText);
                }

                cardContainer.appendChild(cardRating);

                const cardPrice = document.createElement("p");
                cardPrice.textContent = `${product.price}`;
                cardContainer.appendChild(cardPrice);
                if (product.cut_price) {
                  const cardCutPrice = document.createElement("p");
                  cardCutPrice.textContent = `${product.cut_price}`;
                  cardCutPrice.classList.add("card-cut-price");
                  cardContainer.appendChild(cardCutPrice);
                }

                const cardOffer = document.createElement("p");

                if (product.offers && product.offers.length > 0) {
                  const randomIndex = Math.floor(Math.random() * product.offers.length);
                  cardOffer.textContent = `${product.offers[randomIndex]}`;
                } else {
                  cardOffer.textContent = "No offers";
                }

                cardOffer.classList.add("offer");
                cardContainer.appendChild(cardOffer);


                const cardLink = document.createElement("a");
                cardLink.href = product.href;
                cardLink.textContent = "Buy Now";
                cardLink.target = "_blank";
                cardLink.classList.add("card-button");
                cardContainer.appendChild(cardLink);


                platformContainers[platform].appendChild(cardContainer);
                currentRow.appendChild(platformContainers[platform]);

                productCount++;
              }

              const incomingChatDiv = createChatElement(cardWrapper.outerHTML, "incoming");
              chatContainer.appendChild(incomingChatDiv);
            } else {
              const html = `<div class="chat-content">
                                  <div class="chat-details">
                                      <img src="images/chatbot.png" alt="chatbot-img">
                                      <p>I'm sorry, but can you please be more specific?</p>
                                  </div>
                              </div>`;

              const incomingChatDiv = createChatElement(html, "incoming");
              chatContainer.appendChild(incomingChatDiv);
            }

          } else {
            const html = `<div class="chat-content">
                                <div class="chat-details">
                                    <img src="images/chatbot.png" alt="chatbot-img">
                                    <p>I'm sorry, but the API request was not successful.</p>
                                </div>
                            </div>`;

            const incomingChatDiv = createChatElement(html, "incoming");
            chatContainer.appendChild(incomingChatDiv);
          }


        } else {
          const html = `<div class="chat-content">
                              <div class="chat-details">
                                  <img src="images/chatbot.png" alt="chatbot-img">
                                  <p>I'm sorry, but the API request was not successful.</p>
                              </div>
                          </div>`;

          const incomingChatDiv = createChatElement(html, "incoming");
          chatContainer.appendChild(incomingChatDiv);
        }
      } catch (error) {
        console.error(error);
        const html = `<div class="chat-content">
                              <div class="chat-details">
                                  <img src="images/chatbot.png" alt="chatbot-img">
                                  <p>I'm sorry, but I couldn't fetch the product information at the moment. Please try again later.</p>
                              </div>
                          </div>`;

        const incomingChatDiv = createChatElement(html, "incoming");
        chatContainer.appendChild(incomingChatDiv);
      }

    } else {
      const responses = matchedIntent.responses;
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      const responseHtml = html.replace("%response%", randomResponse);
      const responseDiv = createChatElement(responseHtml, "incoming");
      chatContainer.appendChild(responseDiv);
    }
  } else {
    const responses = matchedIntent.responses;
    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    const responseHtml = html.replace("%response%", randomResponse);
    const responseDiv = createChatElement(responseHtml, "incoming");
    chatContainer.appendChild(responseDiv);
  }

  localStorage.setItem("all-chats", chatContainer.innerHTML);
  chatContainer.scrollTo(0, chatContainer.scrollHeight);
};



deleteButton.addEventListener("click", () => {
  // Remove the chats from local storage and call loadDataFromLocalstorage function
  if (confirm("Are you sure you want to delete all the chats?")) {
    localStorage.removeItem("all-chats");
    loadDataFromLocalstorage();
  }
});

themeButton.addEventListener("click", () => {
  // Toggle body's class for the theme mode and save the updated theme to the local storage
  document.body.classList.toggle("light-mode");
  localStorage.setItem("themeColor", themeButton.innerText);
  themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
});

const initialInputHeight = chatInput.scrollHeight;

chatInput.addEventListener("input", () => {
  // Adjust the height of the input field dynamically based on its content
  chatInput.style.height = `${initialInputHeight}px`;
  chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
  // If the Enter key is pressed without Shift and the window width is larger
  // than 800 pixels, handle the outgoing chat
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleOutgoingChat();
  }
});

loadDataFromLocalstorage();

sendButton.addEventListener("click", () => {
  // Handle the outgoing chat
  handleOutgoingChat();
});
