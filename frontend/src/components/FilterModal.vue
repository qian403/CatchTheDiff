<template>
    <div v-if="isOpen" class="modal-overlay" @click.self="close" @keydown.esc="close" role="dialog" aria-modal="true"
        aria-labelledby="filter-modal-title">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="filter-modal-title">篩選與排序</h3>
                <button ref="closeButton" class="close-btn" @click="close" aria-label="關閉篩選視窗">
                    <span class="material-icons" aria-hidden="true">close</span>
                </button>
            </div>

            <div class="modal-body">
                <!-- Sort Options -->
                <div class="filter-section">
                    <h4>排序方式</h4>
                    <div class="radio-group" role="radiogroup" aria-label="排序方式">
                        <label class="radio-label">
                            <input type="radio" v-model="localFilters.sortBy" value="newest" name="sort">
                            <span>最新發布</span>
                        </label>
                        <label class="radio-label">
                            <input type="radio" v-model="localFilters.sortBy" value="recently_changed" name="sort">
                            <span>最近變更</span>
                        </label>
                    </div>
                </div>

                <!-- Date Filter -->
                <div class="filter-section">
                    <h4>日期</h4>
                    <input type="date" v-model="localFilters.date" class="date-input" aria-label="選擇日期">
                </div>

                <!-- Source Filter -->
                <div class="filter-section">
                    <div class="section-header">
                        <h4>媒體來源</h4>
                        <div class="source-actions">
                            <button @click="selectAllSources" class="text-btn" aria-label="選擇所有媒體來源">全選</button>
                            <button @click="clearSources" class="text-btn" aria-label="清除所有媒體來源">清除</button>
                        </div>
                    </div>
                    <div class="sources-grid" role="group" aria-label="媒體來源列表">
                        <label v-for="(name, id) in sources" :key="id" class="checkbox-label">
                            <input type="checkbox" :value="Number(id)" v-model="localFilters.selectedSources"
                                :aria-label="name">
                            <span class="checkbox-text">{{ name }}</span>
                        </label>
                    </div>
                </div>
            </div>

            <div class="modal-footer">
                <button class="reset-btn" @click="resetFilters" aria-label="重置所有篩選條件">重置</button>
                <button class="apply-btn" @click="applyFilters" aria-label="套用篩選條件">套用篩選</button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';

const props = defineProps<{
    isOpen: boolean;
    sources: Record<number, string>;
    currentFilters: {
        sortBy: string;
        date: string;
        selectedSources: number[];
    };
}>();

const emit = defineEmits<{
    (e: 'close'): void;
    (e: 'apply', filters: { sortBy: string; date: string; selectedSources: number[] }): void;
}>();

const localFilters = ref({
    sortBy: 'newest',
    date: '',
    selectedSources: [] as number[]
});

const closeButton = ref<HTMLButtonElement>();

// Sync local state with props when modal opens
watch(() => props.isOpen, async (newVal) => {
    if (newVal) {
        localFilters.value = {
            sortBy: props.currentFilters.sortBy,
            date: props.currentFilters.date,
            selectedSources: [...props.currentFilters.selectedSources]
        };
        // Focus close button for accessibility
        await nextTick();
        closeButton.value?.focus();
    }
});

const close = () => {
    emit('close');
};

const selectAllSources = () => {
    localFilters.value.selectedSources = Object.keys(props.sources).map(Number);
};

const clearSources = () => {
    localFilters.value.selectedSources = [];
};

const resetFilters = () => {
    localFilters.value = {
        sortBy: 'newest',
        date: '',
        selectedSources: []
    };
};

const applyFilters = () => {
    emit('apply', localFilters.value);
    close();
};
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
}

.modal-content {
    background: var(--color-bg-secondary);
    border-radius: var(--radius-lg);
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-xl);
    border: 1px solid var(--color-border);
}

.modal-header {
    padding: var(--spacing-lg);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    color: var(--color-text-tertiary);
    cursor: pointer;
    padding: 4px;
    border-radius: 50%;
    transition: all var(--transition-fast);
}

.close-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--color-text-primary);
}

.modal-body {
    padding: var(--spacing-lg);
    overflow-y: auto;
    flex: 1;
}

.filter-section {
    margin-bottom: var(--spacing-xl);
}

.filter-section h4 {
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-md);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
}

.section-header h4 {
    margin-bottom: 0;
}

.source-actions {
    display: flex;
    gap: var(--spacing-sm);
}

.text-btn {
    background: none;
    border: none;
    color: var(--color-accent-primary);
    font-size: 0.875rem;
    cursor: pointer;
    padding: 2px 8px;
    border-radius: var(--radius-sm);
}

.text-btn:hover {
    background: rgba(59, 130, 246, 0.1);
}

.radio-group {
    display: flex;
    gap: var(--spacing-lg);
}

.radio-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.date-input {
    width: 100%;
    padding: 10px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    color: var(--color-text-primary);
    font-size: 0.875rem;
}

.sources-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm);
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: background var(--transition-fast);
}

.checkbox-label:hover {
    background: rgba(255, 255, 255, 0.05);
}

.checkbox-text {
    font-size: 0.875rem;
}

.modal-footer {
    padding: var(--spacing-lg);
    border-top: 1px solid var(--color-border);
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-md);
}

.reset-btn {
    padding: 8px 16px;
    background: none;
    border: 1px solid var(--color-border);
    color: var(--color-text-secondary);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-fast);
}

.reset-btn:hover {
    border-color: var(--color-text-primary);
    color: var(--color-text-primary);
}

.apply-btn {
    padding: 8px 24px;
    background: var(--color-accent-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-weight: 600;
    cursor: pointer;
    transition: background var(--transition-fast);
}

.apply-btn:hover {
    background: var(--color-accent-secondary);
}

/* Custom Checkbox & Radio Styles */
input[type="checkbox"],
input[type="radio"] {
    accent-color: var(--color-accent-primary);
    width: 16px;
    height: 16px;
}
</style>
