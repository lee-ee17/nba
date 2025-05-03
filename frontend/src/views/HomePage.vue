<template>
    <div class="back">
      <div class="container">
        <img src="@/assets/photos/nba_web_logo.png" class="pic" alt="NBA Logo">
      </div>
      <div class="gr">
        <div>GROUP 6</div>
        <div>NBA VISUALIZATION</div>
        <button class="button-17" role="button" @click="startAnimation">START</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'HomePage',
    methods: {
      startAnimation() {
        const container = document.querySelector('.container')
        const gr = document.querySelector('.gr')
        container.classList.add('fade-out-right')
        gr.classList.add('fade-out-left')

        setTimeout(() => {
          this.$router.push('/select-team')
        }, 1000)
      }
    }
  }
  </script>
  
  <style>
  .back {
    background: linear-gradient(to left, #1c1c1c, #c9c9c9);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    position: relative;
  }
  
  .container {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    transition: all 0.5s ease-in-out;
  }
  
  .pic {
    width: 700px;
    opacity: 0.7;
    margin-left: -400px;
  }
  
  .gr {
    color: aliceblue;
    font-family: system-ui;
    font-size: 40px;
    position: absolute;
    right: 11%;
    top: 55%;
    transition: all 0.5s ease-in-out;
  }
  
  .button-17 {
    position: relative;
    min-width: 160px;
    background: transparent;
    border: none;
    border-radius: 50px;
    font-size: 1rem;
    font-weight: bold;
    text-align: center;
    text-decoration: none;
    text-transform: uppercase;
    padding: 10px 20px;
    color: aliceblue;
    z-index: 1000;
    cursor: pointer;
  }
  
  .button-17 span {
    color: #FFFFFF;
  }
  
  .button-17:before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 52px;
    height: 100%;
    border-radius: 50px;
    background: black;
    transition: all 0.85s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    z-index: -1;
  }
  
  .button-17:hover:before {
    background: black;
    width: 100%;
  }
  
  @keyframes fadeOutRight {
    0% {
      transform: translateX(0);
      opacity: 1;
    }
    100% {
      transform: translateX(100%);
      opacity: 0;
    }
  }
  
  @keyframes fadeOutLeft {
    0% {
      transform: translateX(0);
      opacity: 1;
    }
    100% {
      transform: translateX(-100%);
      opacity: 0;
    }
  }
  
  .fade-out-right {
    animation: fadeOutRight 1s forwards;
  }
  
  .fade-out-left {
    animation: fadeOutLeft 1s forwards;
  }
  </style>