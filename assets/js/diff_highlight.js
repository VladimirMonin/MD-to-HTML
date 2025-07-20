window.syncDiffBlockHeights = () => {
    const diffWrappers = document.querySelectorAll('.diff-wrapper');

    diffWrappers.forEach(wrapper => {
        const beforeContainer = wrapper.querySelector('.diff-container:nth-child(1) pre code');
        const afterContainer = wrapper.querySelector('.diff-container:nth-child(2) pre code');

        if (!beforeContainer || !afterContainer) {
            return;
        }

        // Сбрасываем высоту для пересчета
        beforeContainer.style.height = 'auto';
        afterContainer.style.height = 'auto';

        const beforeHeight = beforeContainer.scrollHeight;
        const afterHeight = afterContainer.scrollHeight;

        const maxHeight = Math.max(beforeHeight, afterHeight);

        beforeContainer.style.height = `${maxHeight}px`;
        afterContainer.style.height = `${maxHeight}px`;
    });
};

// Вызываем синхронизацию при загрузке и изменении размера окна
document.addEventListener('DOMContentLoaded', window.syncDiffBlockHeights);
window.addEventListener('resize', window.syncDiffBlockHeights);