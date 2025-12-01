document.addEventListener("DOMContentLoaded", () => {

  const tutorials = {
    "home-page": "Welcome to your home page! Here you can see your feed.",
    "like-btn": "Click this button to like a post.",
    "bookmark-btn": "Click here to bookmark a post.",
    "view-liked": "View all posts you've liked.",
    "view-bookmarked": "View all posts you've bookmarked.",
    "self-destruct": "This button will self-destruct your database! Use with caution.",
    "add-friend": "Send a friend request using this form.",
    "chat-page": "Click here to go to your chat page.",
    "profile-page": "Click here to view your profile.",
    "log-out": "Click here to log out.",
    "post-btn": "Click here to create a new post."
  };

  // LOAD USERNAME FROM META TAG
  const username = document.querySelector('meta[name="username"]').content;
  const storageKey = `dismissedTutorials_${username}`;

  let dismissed = JSON.parse(localStorage.getItem(storageKey) || "[]");

  Object.keys(tutorials).forEach(key => {
    const elements = document.querySelectorAll(`[data-tutorial="${key}"]`);
    elements.forEach(element => {
      let tooltip = null;
      let isOverTooltipOrButton = false;

      const showTooltip = () => {
        if (dismissed.includes(key) || tooltip) return;

        tooltip = document.createElement("div");
        tooltip.classList.add("tutorial-tooltip");
        tooltip.innerHTML = `
          <span>${tutorials[key]}</span>
          <span class="close-btn">&times;</span>
        `;
        document.body.appendChild(tooltip);

        // FIX: run after DOM paints so offsetHeight is correct
        requestAnimationFrame(() => {
          const rect = element.getBoundingClientRect();
          tooltip.style.top = `${rect.top + window.scrollY - tooltip.offsetHeight - 5}px`;
          tooltip.style.left = `${rect.left + window.scrollX}px`;
        });

        tooltip.addEventListener("mouseenter", () => isOverTooltipOrButton = true);
        tooltip.addEventListener("mouseleave", () => {
          isOverTooltipOrButton = false;
          hideTooltip();
        });

        tooltip.querySelector(".close-btn").addEventListener("click", () => {
          tooltip.remove();
          tooltip = null;
          dismissed.push(key);
          localStorage.setItem(storageKey, JSON.stringify(dismissed));
        });
      };

      const hideTooltip = () => {
        if (tooltip && !isOverTooltipOrButton) {
          tooltip.remove();
          tooltip = null;
        }
      };

      element.addEventListener("mouseenter", () => {
        isOverTooltipOrButton = true;
        showTooltip();
      });

      element.addEventListener("mouseleave", () => {
        isOverTooltipOrButton = false;
        setTimeout(hideTooltip, 50);
      });
    });
  });

});
