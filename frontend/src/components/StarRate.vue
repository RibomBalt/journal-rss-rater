<template>
    <div class="root">
        <div class="star-wrap bottom">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
        <div class="star-wrap mask">
            <div style="width:300px">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        <br />
        <div class="score">
            <span v-if="score !== null" class="score">{{ score }}</span>
            <span v-else class="score">N/A</span>
        </div>
    </div>
   
</template>

<script setup lang="ts">
import { computed, defineModel } from 'vue';

const score = defineModel<number | null>();

const score_width = computed(() => {
    const score_value = score.value ?? 0;
    // 16px + margin-right 4px
    const star_width = 16;
    const star_margin = 4;

    return ((Math.floor(score_value) * star_margin + score_value * star_width) / (5 * star_width + 5 * star_margin) * 100).toString() + '%';
});

</script>


<style scoped>
.root {
    position: relative;
    display: inline-block;
    min-width: 100px;
}

.star-wrap span {
    float: left;
    width: 16px;
    height: 16px;
}

.star-wrap span:not(:last-child) {
    margin-right: 4px;
}

.bottom span {
    background: url(./../assets/star-gray.svg) 0 0 no-repeat;
}

.mask span {
    background: url(./../assets/star-color.svg) 0 0 no-repeat;
}

.mask {
    position: absolute;
    left: 0;
    top: 0;
    overflow: hidden;
    width: v-bind(score_width);
}

.root .score {
    opacity: 0;
    transition: opacity 0.3s;

    width: 50%;
    background-color: #1a2b30;
    color: #fff;
    text-align: center;
    padding: 0px 0;
    border-radius: 6px;
    
    /* Position the tooltip text - see examples below! */
    position: absolute;
    z-index: 1;
}

.root:hover .score {
    opacity: 1;
    transition: opacity 0.3s;
}

</style>